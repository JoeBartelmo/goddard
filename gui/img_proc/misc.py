import cv2
import numpy

def demosaic(input_im):
    '''
    @depricated: Use color_correct instead.
    Originally, we had Econ Cameras, they were not demosaiced and they put 
    a heavy strain on the tk1, so we demosaiced on clientside
    '''
    img_data = numpy.asarray(input_im, dtype=numpy.uint8)
    gray = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(gray, cv2.COLOR_BAYER_GR2RGB)
    return rgb

def color_correct(input_im):
    '''
    Flip color space for Tkinter
    '''
    b,g,r = cv2.split(input_im)
    img = cv2.merge((r,g,b))
    return img

