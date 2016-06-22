import numpy

def average(imgA, imgB, ax=None):
    """ calculate average difference between 2 images. """
    # imgA and imgB: 2 or 3d numpy arrays of the same shape
    # axis: 2 or 3 element tuple indicating which axis to calculate the mean across
    # Notes: n/a

    if imgA.shape != imgB.shape:
        raise ValueError('The input images are not the same shape.') 

    average = (imgA - imgB).mean(axis=ax)
    return average
