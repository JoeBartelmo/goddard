# -*- coding: utf-8 -*-
"""
Created on Mon Jun 06 14:46:34 2016

Use a Kalman Filter to remove noise from an image

This is a first attempt at trying to remove salt and pepper and gaussian 
noise from an image without removing valuable information from the image.
The noise removal method will require a stream of images upon which a discreet
Kalman Filter iteration will operate per pixel (or pixel grouping).
As the state k (frames) increases, noise will be factored out through linear 
quadratic estimation, and the iteration will converge at an estimation of 
the true signal.

DEPENDENCIES
============

Module: cv2, numpy

DEVELOPMENT METADATA
====================

#duh can't do a copyright OR license like this but check with Joe

@copyright:: Copyright (C) 2016 RIT Hyperloop Imaging Team

@license:: LGNU

@author:: Ryan Hartzell

@email:: rah3156@g.rit.edu

@disclaimer:: Neither the members of the RIT Hyperloop Imaging Team nor the 
              Rochester Institute of Technology make any representation 
              about the suitability of this software for any purpose, 
              specifically the ability to prevent catastrophic failures in the
              proposed Hyperloop system. It is provided "as is" without any 
              express or implied warranty whatsoever. The RIT Hyperloop Imaging
              Team will not be liable for any indirect, direct, or 
              consequential damages which may result from the use of this
              software.
              
HISTORY
=======

1.0.dev1
    * [06 June 2016 : Ryan Hartzell] 
        * Noise reduction method, documentation, and initial test harness prep
        
"""

#import urllib2
#import cStringIO
#import numpy as np
#import mahotas as mh
import cv2

def kalman_noise_reduc(stream):

    """
    A method for reducing Gaussian noise in an image by Kalman Filtering
    """
    #If this stream can be accessed through a URL which is probably not the
    #the case. If we can figure out the 'capture from stream' method then
    #I might not even need to write this in myself
    
#    file = cStringIO.StringIO(urllib2.urlopen(stream).read())
#    imgCurrent = cv2.imread(file)
#    #cv2.imshow(imgCurrent)
    
    #OR
    
    k = 0 #set initial state of Kalman Filter given first frame
    
    cap = cv2.VideoCapture(stream)
    while(cap.isOpened()):
        
        #Grab the current image from the stream and set as frame
        ret, frame = cap.read()
        #NOTE: WE MAY ALSO NEED TO MAKE THIS FRAME A NUMPY ARRAY
        #We need to make the images greyscale
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
    #^^^^^This can read from image sequences which I assume means a stream
    #if not, we can always use the commented out method above to proceedurally
    #save images from the stream to a temporary file, operate on them, and 
    #then repeat the process but with the new "input" which was the last Kalman
    #filter output

        #set up a variable that is an empty array the size of frame. We'll put
        #the new, adjusted (noiseless) image here
        frame_adj = gray * 0

    #Great, now we can start the real math. Maybe.

    #Start by cycling through the image and doing the operation on a per pixel
    #basis. This will allow us to continue to think of this as a single
    #dimension linear system across deltas in time measured by frame
        for n in range(frame.shape[0]):
            for m in range(frame.shape[1]):
                if k == 0:
                    x_hat_est = 0
                    p_k_est = 1
                    
                else:
                    x_hat_est = x_hat_adj
                    p_k_est = p_k_adj
                    
                #Now we can index into the correct code values at the pixel and
                #do the calculation
                
                #We must make an approximaition for std. dev. of noise, R
                R = 1 #This is a constant that we can change during testing                
                
                #Calculate Kalman Gain
                K_gain = p_k_est/(p_k_est + R)
                
                #Calculate adjusted x_hat and p_hat utilizing code value of pix
                #as our measured value z_k
                
                z_k = frame[n,m] #should return a single code value 0-255 Grey
                x_hat_adj = x_hat_est + K_gain*(z_k - x_hat_est)
                p_k_adj = (1 - K_gain)*p_k_est
                
                """
                I STILL NEED TO WRITE A WAY TO LOG THE FINAL VALUE DELIVERED BY
                THIS FUNCTION, WHICH SHOULD BE THE SIGNAL FOR EACH PIXEL, AND I
                NEED TO APPEND EACH OF THESE "CORRECTED VALUES" TO A VECTOR OR
                ARRAY WHICH WE CAN TURN INTO AN IMAGE. HOPING NATE CAN HELP ME
                WITH THIS, BC MY ARRAY SKILLS HAVE DETERIORATED PRETTY BADLY.
                
                FUNCTION ITSELF IS PRETTY MUCH DONE, BUT THE EXTRA STUFF LIKE 
                INPUT/OUTPUT NEEDS SOME WORK.
                """
                
                frame_adj[n,m] = x_hat_adj
                
        #We also need to send this adjusted frame on its way before the next
        #one gets sent through.
                
        #cv2.imwrite('frame_adj',#send to gui stuff)
        
        #for TESTING ONLY: This will display the image until the user hits Esc
        #or until they hit 
        cv2.imshow('Kalman Filter for the state k = ' + str(k),frame_adj)
        
        key = cv2.waitKey(0) & 0xFF #as specified by the waitKey documentation
        print 'Hit \'Esc\' to destroy the window, or \'s\' to save the image.'

        if key == 27:         # wait for ESC key to exit
            cv2.destroyAllWindows()
        elif key == ord('s'): # wait for 's' key to save and exit
            cv2.imwrite('KalmanIteration_' + str(k) + '.png',frame_adj)
            cv2.destroyAllWindows()
        
        #at the end of everything, set state for next frame
        k += 1

#end of stream reading and release. again, I might not even have to write all
#this, but we still need a method or class we can reference to do this then
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    imSequence = [] #images should go in here