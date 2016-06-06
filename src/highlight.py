import numpy
import cv2

def highlight(img, pixels, channel, alpha=0.7):
    """ highlight pixels in image of channel. """
    # img: numpy or opencv 3 channeled image
    # pixels: 2d boolean array, same shape` as img
    # channel: channel (or color) to draw in
    # alpha: how transparent to make the drawing, 0-1 (1 is opaque)

    overlay = img.copy()
    val = numpy.array([0, 0, 0])
    val[channel] = 255
    overlay[pixels] = val
    
    cv2.addWeighted(overlay, alpha, img, 1 - alpha,
		0, img)

    return img

if __name__=='__main__':
    img = cv2.imread('elon_2_copy2.jpg',1)

    output = highlight(img, numpy.where(img[:,:,0]>200), 2)

    cv2.namedWindow(' ')
    cv2.imshow(' ', output)
    cv2.waitKey(10000)
    
