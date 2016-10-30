# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import Tkinter as tk
from PIL import Image, ImageTk
import cv2
import sys
import numpy
import time
import matplotlib.path as matpath

class GlobalSurveyor(object):
    def __init__(self, root, ideal_image,  number_polys = 2, thresholds = (50, 200), polys = None):
        self.ideal_im = ideal_image
        self.parent = root
        self.done = False
        self.points = []
        self.warningColor = (128, 128, 0)
        self.errorColor = (255, 0, 0)

        self.number_polys = number_polys
        #self.number_sides = number_sides
        if polys == None:
            self.polys = []
        else:
            self.polys = polys

        self.thresh = thresholds
        self.ideal_counts = []
        self.calibrates_polygons()

    def calibrates_polygons(self):
        polys = self.define_polygons(self.ideal_im)
        ideal_kp = self.apply_fast(self.ideal_im)
        self.ideal_counts = self.keypoints_to_counts(ideal_kp)

    def _on_left_mouse(self, event):   # CITE THIS FROM STACKEXCHANGE
        # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)
        if self.done: # Nothing more to do
            return
        # Left click means adding a point at current position to the list of points
        print("Adding point #%d with position(%d,%d)" % (len(self.points), event.x, event.y))
        self.points.append((event.x, event.y))

    def _on_right_mouse(self, event):   # CITE THIS FROM STACKEXCHANGE
        if len(self.points) > 2:
            # Right click means we're done
            print("Completing polygon with %d points." % len(self.points))
            self.done = True

    def define_polygons(self, image):
        # use this to automate point picking and/or display point picker window in gui

        FINAL_LINE_COLOR = (255, 0, 0)
        WORKING_LINE_COLOR = (0, 0, 255)

        top = tk.Toplevel(self.parent)
        top.title("Select bounding points for the target area")
        print image.shape
        top.update_idletasks()
        width = image.shape[1]
        height = image.shape[0]
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        #we are defaulting to the image size, i don't want to deal wiht resizing
        initial_im = tk.PhotoImage()
        image_label = tk.Label(top, image=initial_im)
        image_label.grid(row = 0, column = 0)
        image_label.bind("<Button-1>", self._on_left_mouse)
        image_label.bind("<Button-3>", self._on_right_mouse)
        top.grid()

        copy = image.copy()
        def display_image():
            imageFromArray = Image.fromarray(copy)
            try:
                tkImage = ImageTk.PhotoImage(image=imageFromArray)
                image_label.configure(image=tkImage)
            
                image_label._image_cache = tkImage  # avoid garbage collection

                top.update()
                return True
            except RuntimeError:
                print('Unable to update image frame. Assuming application has been killed unexpectidly.')
                return False

        for num in range(self.number_polys):
            if display_image() == False:
                top.destroy()
                return

            self.points = []
            self.done = False

            while (not self.done):
                if (len(self.points) > 0):
                    cv2.polylines(copy, numpy.asarray([self.points]), False, FINAL_LINE_COLOR, 1)

                imageFromArray = Image.fromarray(copy)
                if display_image() == False:
                    top.destroy()
                    return
            self.polys.append(self.points)
            print(self.polys)
            update = numpy.asarray(self.polys[num]).astype(numpy.int32)
            
            if (len(self.points) > 0):
                cv2.fillPoly(copy, [update], (0,0,255))
        display_image()

        time.sleep(0.5)
        top.destroy()

        return self.polys

    def apply_fast(self, image):
        fast = cv2.FastFeatureDetector()
        kp = fast.detect(image, None)

        return kp

    def keypoints_to_counts(self, im_keypoints): #polys = numpy.asarray[[[0,0],[0,ideal_im.shape[0]//2],[ideal_im.shape[0]//2,ideal_im.shape[1]],[ideal_im.shape[0]//2, 0]]]):
        #pass in im_keypoints and count how many are in each polygon
        #polygon points should also be an input

        im_keys = []
        for i in range(len(im_keypoints)):
            im_keys.append(im_keypoints[i].pt)

        # NOTE:: POLYS MUST BE IN X (COL), Y (ROW) FORMAT FOR FILLPOLY TO WORK

        # NOTE:: POLYS MUST ALSO BE OF DTYPE FLOAT
        
        data = self.polys
        polys = map(lambda data: map(lambda data: map(float, data), data), data)
        counts = []

        for poly in polys:
            # MATPLOTLIB PATH EXAMPLE GOES HERE
            bbPath = matpath.Path(poly)
            # sum boolean array to get number of kp within current poly
            try:
                truth_vector = bbPath.contains_points(im_keys)   # check input for contains_points. might only like tuples
            except:
                truth_vector = [1] * len(im_keys)
            counts.append(numpy.sum(truth_vector))

        return numpy.asarray(counts)

    def threshold(self, counts, thresh_tuple):
        # do the thresholding thing
        delta = abs(counts - self.ideal_counts)

        threshed_polys = numpy.where((delta >= thresh_tuple[0]) & (delta < thresh_tuple[1]))[0]   # ok to index like this because tuple represents vector
        
        # save which polys get marked true out so these can be used as overlay in fillpolys
        # this can be done by indexing into polys with truth vector saved here

        return threshed_polys.astype(int)   # a true/false vector of length polys

    def generate_output(self, image, threshed_polys, color, alpha = 0.5): #, colorAlert = (0,0,255)):
        # use polyfill to blend im_in and overlay (which is just the polygons we want colored in)
        colored_polys = []

        for threshed_poly in threshed_polys:
            colored_polys.append(numpy.array(self.polys[threshed_poly]).astype(numpy.int32))

        overlay = image.copy()
        im_out = image.copy()

        for cp in range(len(colored_polys)):
            cv2.fillPoly(overlay, [colored_polys[cp]], color)
        
        cv2.addWeighted(overlay, alpha, im_out, 1 - alpha, 0, im_out)

        return im_out

    def run_basic_fod(self, current_im):
        if current_im is None:
            return None
        # load ideal image
        im_in_kp = self.apply_fast(current_im)

        counts = self.keypoints_to_counts(im_keypoints = im_in_kp)

        warning_polys = self.threshold(counts, self.thresh)
        error_polys = self.threshold(counts, (self.thresh[1], sys.maxint))

        warning_overlay = self.generate_output(current_im, warning_polys, self.warningColor)
        return self.generate_output(warning_overlay, error_polys, self.errorColor)

def get_thresholds_widget(parent):
    top = tk.Toplevel(parent)
    top.title("Select your desired thresholds")
    top.update_idletasks()

    done = False
    thresh1 = tk.IntVar()
    thresh2 = tk.IntVar()
    polys = tk.IntVar()

    #3 labels and 3 textbox selectors
    label1 = tk.Label(top, text = "Warning (Maybe an object)")
    label1.grid(row = 1, column = 0, sticky ="nsew")
    threshold1 = tk.Entry(top, textvariable=thresh1)
    threshold1.grid(row = 1, column = 1, sticky ="nsew")
    
    label2 = tk.Label(top, text = "Error (Most defintely an object)")
    label2.grid(row = 2, column = 0, sticky ="nsew")
    threshold2 = tk.Entry(top, textvariable = thresh2)
    threshold2.grid(row = 2, column = 1, sticky ="nsew")

    label3 = tk.Label(top, text = "Number of Polygons")
    label3.grid(row = 3, column = 0, sticky ="nsew")
    threshold3 = tk.Entry(top, textvariable = polys)
    threshold3.grid(row = 3, column = 1, sticky ="nsew")

    def returnVars():
        top.destroy()
        global done
        done = True
    
    button = tk.Button(top, text = "Set Values", command = returnVars)
    button.grid(row = 4, column = 0, columnspan = 2, sticky ="nsew")

    threshold1.delete(0, "end")
    threshold1.insert(0, 50)
    threshold2.delete(0, "end")
    threshold2.insert(0, 200)
    threshold3.delete(0, "end")
    threshold3.insert(0, 2)

    width = 300
    height = 100
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    top.grid_columnconfigure(1, weight=1)
    top.grid_rowconfigure(0, weight=1)
    top.grid_rowconfigure(1, weight=1)
    top.grid()
    top.update()

    while not done:
        time.sleep(0.1)
    return (int(thresh1), int(thresh2), int(polys))
    
if __name__=='__main__':

    import cv2
    import os.path
    import time

    home = os.path.expanduser('~')
    ideal = home + os.path.sep + 'Documents/HyperloopSoftwareDev/hidden_valley/rail_top_rough.png'
    im_in = home + os.path.sep + 'Documents/HyperloopSoftwareDev/hidden_valley/rail_top_rough_messy.png'

    im1 = cv2.imread(ideal, cv2.IMREAD_UNCHANGED)
    im2 = cv2.imread(im_in, cv2.IMREAD_UNCHANGED)

    # IDEAL INSTANCE

    ideal = GlobalSurveyor(im1, 2)

    # USE IDEAL IM TO CALCULATE POLYS (DONE ONCE)

    polys = ideal.define_polygons()

    # CALCULATE IDEAL KPs

    ideal_kp = ideal.apply_fast()

    # CALCULATE IDEAL COUNTS

    ideal.keypoints_to_counts(im_keypoints = ideal_kp)

    current = GlobalSurveyor(im2, polys = polys)

    im_in_kp = current.apply_fast()

    current.keypoints_to_counts(im_keypoints = im_in_kp)

    threshed_polys = current.threshold(ideal.counts)

    print threshed_polys

    im_out = current.generate_output(threshed_polys)

    cv2.imshow('ideal', im1)
    cv2.waitKey(10000000)
    
    cv2.imshow('live', im_out)
    cv2.waitKey(10000000)
