import numpy

def line_det():
    pass

def pumpkin():
    pass


if __name__=='__main__':
    import cv2
    
    a = cv2.imread('elon_2_copy2.jpg', 0)
    b = cv2.imread('elon_2_finalcopy_unmod.jpg', 0)
    
    
    cv2.namedWindow('bob')

    x = 2
    
    a_blocks = block_img(a, x_block_size=x, y_block_size=x)
    b_blocks = block_img(b, x_block_size=x, y_block_size=x)
    

    cv2.imshow('bob', output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('output.jpg', output)
