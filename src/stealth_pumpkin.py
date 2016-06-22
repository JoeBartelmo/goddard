import block
import numpy
import cv2

def stealth_pumpkin(img1, img2):
    return img1.mean() - img2.mean()

def auto_canny(image, sigma=0.33):

	# compute the median of the single channel pixel intensities
	v = numpy.median(image)

	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)

	# return the edged image
	return edged

def script(in_q, out_q1, out_q2):
    # load ideal image
    ideal_image = cv2.imread('/home/nathan/python/PyDetect/src/client/assets/webcam_edges.jpg')

    block_size = 8
    ideal_image_blocks = block.block_img(ideal_image, x_block_size=block_size, y_block_size=block_size)

    while True:
        q_image = in_q.get()

        if type(q_image) is not numpy.ndarray or q_image is None:
            print 'wrong type'
            continue
 
        q_image = auto_canny(q_image)   # TODO line detection
        q_img_blocks = block.block_img(q_image, x_block_size=block_size, y_block_size=block_size)

        pumpkins = []

        for k in range(len(q_img_blocks)):
            pumpkins.append(stealth_pumpkin(q_img_blocks[k], ideal_image_blocks[k]))
        
        pumpkins = numpy.absolute(numpy.asarray(pumpkins))
        pumpkins = ((pumpkins / numpy.amax(pumpkins)) * 255)

        pumpkins_img = numpy.reshape(pumpkins, (q_image.shape[0] / block_size, q_image.shape[1] / block_size ))
        # TODO deblock
        out_q1.put(pumpkins_img)

        # TODO choose indices better
        indices = numpy.where(pumpkins_img > 128 )
        out_q2.put(indices)


