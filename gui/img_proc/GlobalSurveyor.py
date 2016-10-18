import cv2
import numpy
import matplotlib.path as matpath

class GlobalSurveyor(object):
	def __init__(self, im, number_polys = 5, threshold = 20, polys = None):
		self.im = im

		self.done = False
		self.current_pt = (0,0)
		self.points = []

		self.number_polys = number_polys
		#self.number_sides = number_sides
		if polys == None:
			self.polys = []
		else:
			self.polys = polys

		self.counts = []
		self.thresh = threshold

	def _on_mouse(self, event, x, y, buttons, user_param):   # CITE THIS FROM STACKEXCHANGE
		# Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)

		if self.done: # Nothing more to do
			return

		#if event == cv2.EVENT_MOUSEMOVE:
			# We want to be able to draw the line-in-progress, so update current mouse position
			#self.current_pt = (x, y)
		elif event == cv2.EVENT_LBUTTONDOWN:
			# Left click means adding a point at current position to the list of points
			print("Adding point #%d with position(%d,%d)" % (len(self.points), x, y))
			self.points.append((x, y))
		elif event == cv2.EVENT_RBUTTONDOWN:
			# Right click means we're done
			print("Completing polygon with %d points." % len(self.points))
			self.done = True

	def define_polygons(self):
		# use this to automate point picking and/or display point picker window in gui

		FINAL_LINE_COLOR = (255, 0, 0)
		WORKING_LINE_COLOR = (0, 0, 255)

		imName = 'Select bounding points for the target area (CW)'
		cv2.namedWindow(imName, cv2.WINDOW_AUTOSIZE)

		copy = self.im.copy()
		cv2.cv.SetMouseCallback(imName, self._on_mouse)

		for num in range(self.number_polys):
			cv2.imshow(imName, copy)

			self.points = []
			self.done = False

			while (not self.done):
				if (len(self.points) > 0):
					cv2.polylines(copy, numpy.asarray([self.points]), False, FINAL_LINE_COLOR, 1)
					#cv2.line(copy, self.points[-1], self.current_pt, WORKING_LINE_COLOR)

				cv2.imshow(imName, copy)

				if cv2.waitKey(50) == 27: # ESC
					self.done = True

			self.polys.append(self.points)
			print(self.polys)
			update = numpy.asarray(self.polys[num]).astype(numpy.int32)
			
			if (len(self.points) > 0):
				cv2.fillPoly(copy, [update], (0,0,255))

		cv2.imshow(imName, copy)
		cv2.waitKey()
		cv2.destroyWindow(imName)

		return self.polys

	def apply_fast(self):
		fast = cv2.FastFeatureDetector()
		kp = fast.detect(self.im, None)

		return kp

	def keypoints_to_counts(self, im_keypoints): #polys = numpy.asarray[[[0,0],[0,ideal_im.shape[0]//2],[ideal_im.shape[0]//2,ideal_im.shape[1]],[ideal_im.shape[0]//2, 0]]]):
		#pass in im_keypoints and count how many are in each polygon
		#polygon points should also be an input

		print len(im_keypoints)

		im_keys = []
		for i in range(len(im_keypoints)):
			im_keys.append(im_keypoints[i].pt)

		# NOTE:: POLYS MUST BE IN X (COL), Y (ROW) FORMAT FOR FILLPOLY TO WORK

		# NOTE:: POLYS MUST ALSO BE OF DTYPE FLOAT
		
		data = self.polys
		polys = map(lambda data: map(lambda data: map(float, data), data), data)

		for poly in polys:
			# MATPLOTLIB PATH EXAMPLE GOES HERE
			print poly
			bbPath = matpath.Path(poly)
			# sum boolean array to get number of kp within current poly

			truth_vector = bbPath.contains_points(im_keys)   # check input for contains_points. might only like tuples
			self.counts.append(numpy.sum(truth_vector))
			print self.counts	

		return numpy.asarray(self.counts)

	def threshold(self, ideal_counts):
		# do the thresholding thing

		delta = abs(numpy.asarray(self.counts) - numpy.asarray(ideal_counts))

		print delta

		threshed_polys = numpy.where(delta >= self.thresh)[0]   # ok to index like this because tuple represents vector

		# save which polys get marked true out so these can be used as overlay in fillpolys
		# this can be done by indexing into polys with truth vector saved here

		return threshed_polys.astype(int)   # a true/false vector of length polys

	def generate_output(self, threshed_polys, alpha = 0.5, colorWarning = (0,125,125)): #, colorAlert = (0,0,255)):

		# use polyfill to blend im_in and overlay (which is just the polygons we want colored in)

		colored_polys = []

		for threshed_poly in threshed_polys:
			colored_polys.append(numpy.array(self.polys[threshed_poly]).astype(numpy.int32))

		print colored_polys

		overlay = self.im.copy()
		im_out = self.im.copy()

		for cp in range(len(colored_polys)):
			cv2.fillPoly(overlay, [colored_polys[cp]], colorWarning)
		
		cv2.addWeighted(overlay, alpha, im_out, 1- alpha, 0, im_out)

		return im_out

def script(ideal_im, current_im):
	# load ideal image

	ideal = GlobalSurveyor(ideal_im, 2)

	polys = ideal.define_polygons()

	ideal_kp = ideal.apply_fast()

	ideal.keypoints_to_counts(im_keypoints = ideal_kp)

	current = GlobalSurveyor(current_im, polys = polys)

	im_in_kp = current.apply_fast()

	current.keypoints_to_counts(im_keypoints = im_in_kp)

	threshed_polys = current.threshold(ideal.counts)

	return current.generate_output(threshed_polys)

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