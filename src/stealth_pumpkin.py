import block
import numpy
import cv2
import highlight
import math

def stealth_pumpkin(img, img_keypoints, block_size=8):
    
    counts = numpy.zeros((img.shape[0:2]))
    r = block_size / 2

    for kp in img_keypoints:
        x = kp.pt[0]
        y = kp.pt[1]

        counts[x-r:x+r, y-r:y+r] += 1

    return counts
    
def sneaky_squash(ideal_counts, frame_counts, threshold=0):
    delta = numpy.absolute(ideal_counts - frame_counts)
    return numpy.where(delta > threshold)

def script(in_q, out_q1):
    # load ideal image
    ideal_image = cv2.imread('/home/nathan/python/PyDetect/src/client/assets/webcam.jpg')

    fast = cv2.FastFeatureDetector()

    ideal_image_kp = fast.detect(ideal_image, None)
    pump = stealth_pumpkin(ideal_image, ideal_image_kp)

    while True:
        q_image = in_q.get()

        if type(q_image) is not numpy.ndarray or q_image is None:
            print 'wrong type'
            continue
 
        q_image_kp = fast.detect(q_image, None)
        squash = stealth_pumpkin(q_image, q_image_kp)

        pumpkins_indexes = sneaky_squash(pump, squash)

        out_image = highlight.highlight(q_image, pumpkins_indexes, color=(255,0,0))
        out_q1.put(out_image)


if __name__=='__main__':
    v = cv2.VideoCapture(0)

    f, frame = v.read()
    fast = cv2.FastFeatureDetector()
    ideal_image_kp = fast.detect(frame, None)
    pump = stealth_pumpkin(frame, ideal_image_kp)
    
    for i in range(60):
        f, frame = v.read()

    raw_input('Press Enter')
    f, frame2 = v.read()
    frame_kp = fast.detect(frame2, None)

    squash = stealth_pumpkin(frame, frame_kp)

    pumpkins_indexes = sneaky_squash(pump, squash)

    out_image = highlight.highlight(frame2, pumpkins_indexes, color=(255,0,0))

    cv2.imshow('', out_image)
    cv2.waitKey(0)
