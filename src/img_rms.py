import numpy

def rms(imgA, imgB, ax=None):
    """ calculate root mean square between 2 images. """
    # imgA and imgB: 2 or 3d numpy arrays of the same shape
    # axis: 2 or 3 element tuple indicating which acis to calculate the mean across
    # Notes: n/a

    if imgA.shape != imgB.shape:
        raise ValueError('The input images are not the same shape.') 

    rms = ((imgA - imgB) ** 2).mean(axis=ax)
    return rms

def block_img(img, x_block_size=100, y_block_size=100, x_offset=0, y_offset=0):
    """ split image up into evenly sized blocks. """
    # img: a 2 or 3d numpy array of type uint8
    # the rest are self explanatory 
    blocks = []

    for i in range(x_offset,img.shape[0],x_block_size):
        for j in range(y_offset, img.shape[1],y_block_size):
            blocks.append(img[i:i+x_block_size,j:j+y_block_size])

    return blocks

        
if __name__=='__main__':
    import cv2
    a=cv2.imread('elon_2_finalcopy.jpg', 0)
    b=cv2.imread('elon_2_finalcopy_unmod.jpg', 0)
    
    a_b_rms = rms(a, b)
    print rms(a, b)
    print rms(a, b, 0)
    print a.shape
    #print rms(a[400:-1,400:-1,1], b[400:-1, 400:-1, 1])

    cv2.namedWindow('bob')
    #cv2.namedWindow('bob1')

    #cv2.imshow('bob1', a)

    x = 2
    
    a_blocks = block_img(a, x_block_size=x, y_block_size=x)
    b_blocks = block_img(b, x_block_size=x, y_block_size=x)
    rms_s = []

    for k in range(len(a_blocks)):
        rms_s.append(rms(a_blocks[k], b_blocks[k]) - a_b_rms)
        
    rms_s = numpy.absolute(numpy.array(rms_s))
    rms_img = ((rms_s / numpy.amax(rms_s)) * 255)
    rms_img = numpy.reshape(rms_img, (a.shape[0] / x + 1, a.shape[1] / x ))
    #rms_img[0:100, 0:100] = 0
    print rms_img.shape
    print rms_img.mean()
    cv2.imshow('bob', rms_img)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
