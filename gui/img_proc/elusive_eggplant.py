import cv2
import numpy
import matplotlib.path as matpath
import PointsSelected

'''
class HiddenValley(object):

	def __init__(image):
		self.image = image
		self.x = []
		self.y = []
		self.polygons = []
'''

def phantom_pickle(im, number_polys = 5):
	# use this to automate point picking and/or display point picker window in gui
	imName = 'Select corners for the target area (CW)'
	cv2.namedWindow(imName, cv2.WINDOW_AUTOSIZE)

	x = []
	y = []

	copy = im.copy()

	for num in range(number_polys):
		cv2.imshow(imName, copy)
		p = PointsSelected.PointsSelected(imName, verbose=True)
		while p.number() < 4:
			#cv2.drawCircle()
			cv2.waitKey(100)
		x.append(p.x())
		y.append(p.y())
		update = numpy.asarray(zip(x[num],y[num])).astype(numpy.int32)
		cv2.fillPoly(copy, [update], (0,0,255))
		p.reset()

	cv2.destroyWindow(imName)

	polys = []

	for poly in range(len(x)):
		polys.append(zip(x[poly], y[poly]))

	return polys

def elusive_eggplant(im_keypoints, polys): #polys = numpy.asarray[[[0,0],[0,ideal_im.shape[0]//2],[ideal_im.shape[0]//2,ideal_im.shape[1]],[ideal_im.shape[0]//2, 0]]]):
	#pass in im_keypoints and count how many are in each polygon
	#polygon points should also be an input

	print len(im_keypoints)

	im_keys = []
	for i in range(len(im_keypoints)):
		im_keys.append(im_keypoints[i].pt)

	# NOTE:: POLYS MUST BE IN X (COL), Y (ROW) FORMAT FOR FILLPOLY TO WORK

	#polys = numpy.asarray([[(0,0),(960, 0),(960, 540),(0, 540)]]).astype(float)
	polys = numpy.asarray(polys).astype(float)
	#polys = [[],[],[],[],[],[]]   # fill these when testing, move to testharness and pass in as param

	counts = []

	for poly in polys:
		# MATPLOTLIB PATH EXAMPLE GOES HERE
		print poly
		bbPath = matpath.Path(poly)
		# sum boolean array to get number of kp within current poly
		# store in vector of counts[poly]

		truth_vector = bbPath.contains_points(im_keys)   # check input for contains_points. might only like tuples
		counts.append(numpy.sum(truth_vector))
		print counts	

	return numpy.asarray(counts) #polys   # THIS METHOD ONLY HANDLES COUNTS, returns polys for use in highlighting

def coniving_carrot(ideal_counts, counts, thresh1 = 10):   # , thresh2 = 10):
	# do the thresholding thing (basically sneaky_squash)

	delta = abs(counts - ideal_counts)

	print delta

	threshed_polys = numpy.where(delta >= thresh1)[0]   # ok to index like this because tuple represents vector

	# save which polys get marked true out so these can be used as overlay in fillpolys
	# this can be done by indexing into polys with truth vector saved here

	return threshed_polys.astype(int)   # a true/false vector of length polys

def sly_spinach(im_in, threshed_polys, polys, alpha = 0.5, colorWarning = (0,125,125)): #, colorAlert = (0,0,255)):

	# use polyfill to blend im_in and overlay (which is just the polygons we want colored in)

	polys = numpy.asarray(polys)
	colored_polys = polys[threshed_polys].astype(numpy.int32)

	print colored_polys

	overlay = im_in.copy()
	im_out = im_in.copy()

	cv2.fillPoly(overlay, colored_polys, colorWarning)
	cv2.addWeighted(overlay, alpha, im_out, 1- alpha, 0, im_out)

	return im_out

def script(im_in, im_out):
	# load ideal image
	ideal_image = im_in.get()

	fast = cv2.FastFeatureDetector()

	ideal_kp = fast.detect(ideal_image, None)
	ideal_counts = elusive_eggplant(ideal_image, ideal_kp)

	while True:
		im_in = im_in.get()

		if type(im_in) is not numpy.ndarray or im_in is None:
			print 'wrong type'
			continue

		im_in_kp = fast.detect(im_in, None)

		#k nearest neighbors here?

		counts, polys = elusive_eggplant(ideal_image, im_in_kp)

		threshed_polys = coniving_carrot(ideal_kp, counts)

		im_out = sly_spinach(im_in, threshed_polys, polys)

		im_out.put(out_image)

if __name__=='__main__':

	import cv2
	import os.path
	import time

	home = os.path.expanduser('~')
	ideal = home + os.path.sep + 'Documents/HyperloopSoftwareDev/hidden_valley/rail_top_rough.png'
	im_in = home + os.path.sep + 'Documents/HyperloopSoftwareDev/hidden_valley/rail_top_rough_messy.png'

	im1 = cv2.imread(ideal, cv2.IMREAD_UNCHANGED)
	im2 = cv2.imread(im_in, cv2.IMREAD_UNCHANGED)

	polys = phantom_pickle(im1, number_polys = 5)

	fast = cv2.FastFeatureDetector()

	ideal_kp = fast.detect(im1, None)
	ideal_counts = elusive_eggplant(im_keypoints = ideal_kp, polys = polys)

	im_in_kp = fast.detect(im2, None)

	counts = elusive_eggplant(im_keypoints = im_in_kp, polys = polys)

	threshed_polys = coniving_carrot(ideal_counts, counts)

	print threshed_polys

	im_out = sly_spinach(im2, threshed_polys, polys)

	cv2.imshow('ideal', im1)
	cv2.waitKey(10000000)
	
	cv2.imshow('live', im_out)
	cv2.waitKey(10000000)