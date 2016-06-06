import numpy

def rms(imgA, imgB, ax=None):
    """ calculate root mean square between 2 images. """
    # imgA and imgB: 2 or 3d numpy arrays of the same shape
    # axis: 2 or 3 element tuple indicating which axis to calculate the mean across
    # Notes: n/a

    if imgA.shape != imgB.shape:
        raise ValueError('The input images are not the same shape.') 

    rms = ((imgA - imgB) ** 2).mean(axis=ax)
    return rms

        
if __name__=='__main__':
    import cv2

    a = cv2.imread('elon_2_copy2.jpg', 0)
    b = cv2.imread('elon_2_finalcopy_unmod.jpg', 0)
    
    a_b_rms = rms(a, b)
    print a_b_rms
    print a.shape

    cv2.namedWindow('bob')

    x = 2
    
    a_blocks = block_img(a, x_block_size=x, y_block_size=x)
    b_blocks = block_img(b, x_block_size=x, y_block_size=x)
    rms_s = []

    for k in range(len(a_blocks)):
        rms_s.append(rms(a_blocks[k], b_blocks[k]))
        
    rms_s = numpy.absolute(numpy.array(rms_s))
    rms_img = ((rms_s / numpy.amax(rms_s)) * 255)
    rms_img = numpy.reshape(rms_img, (a.shape[0] / x + 1, a.shape[1] / x ))
    
    print rms_img.shape
    print rms_img.mean()

    cv2.imshow('bob', rms_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('output.jpg', rms_img)
