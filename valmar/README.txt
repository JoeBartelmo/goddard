Valmar is a very complex system, as such I will detail more precisely what goes on in here, this is strictly a technical overview.


This program is written in c++ becuase we need to utilize the tegra optimization to keep this as fast as possible. We are consuming 100-500 fps
on the Ximea cameras (each) and speed is of the essence, therefore you will see precompiler command debug statements to avoid bogging down the 
time of the program. Thus, rather than write python bindings and painful attempt to optimize python, lets just do c++ and find some way to 
communicate with python. (decided on a named pipe)



Resources: 
    Valmar uses OpenCV2 (Tegra optimzied), xiAPI, and several other built in C-libraries.

Testing locally: 
    Unfortunetly, because of how tightly coupled this system is, you will have a hard time testing locally, compiling locally I have built in however

    "make local"
    I typically use this for testing before i commit something


Calibration: (probably wont need to be done each test run) -- requires monitor hooked up to tk1

    "make calibrate"

    Calibration was primarily written by Nate. Essentially, we pass in either hte left or right camera as a commandline argument. I have configured
    the code so that it will run either camera in the same way that Valmar does (you can update real time). The image the ximea is outputting will
    then appear on the screen with the help of opencv. Instructions will be in the terminal from thereon out.

    Calibration uses the "calibration" section of the command.json file to determine checkerboard size and distance of a SINGLE square on a
    checkerboard.

    It will output an opencv native file "yml" prepended with the camera name. This yml file will contain distortion coefficients to apply
    to each frame that we process with our greedy algorithm. It will also supply us with the pixel-inches ratio for the camera.

Valmar:

    "make"

    Valmar will require both cameras to be plugged in, otherwise you will get a failure on opening the program. Once both cameras are plugged in we
    open up a connection to a named pipe, location determined by command.json. The pipe will be read from by the mars package, so as to keep valmar as
    loosley coupled as we can. However, if you are not working directly with mars, you will not need this functionality, and valmar will simply hang,
    waiting for the receiving end of the pipe. Thus, we have a seperatly compiled module "valmar-debug" that you should run instead if you just want to
    test locally. Currently this is how we determine our proper thresholds for the greedy algorithm. 


    Details on Settings Thresholds:
        This should occur strictly after camera calibration. We have yet to develop a method to automatically determine thresholds, however with time
        and trial and error, such a method could be developed. Essentially, we want to place MARS overtop of a beam such that the cameras are near the
        intersection of two beams, but not overtop.

        We apologize for such a tedious process, but this should only need to happen once.

        Launch mars program with "python run.py settings.json" and type "valmar off" then "brightness 9". 
        In another terminal window, launch valmar-debug, in another terminal window, open up "command.json" in vim.

        Everything is ready to start calibrating. Take a look at the "Command.json" section to figure out what to calibrate.

        To trigger the threshold, slowly move mars overtop of a beam_gap. If the sumThreshold is properly configured, you should see a lot of 
        pretty opencv windows pop up with varying names according to the point at which the algorithm is processing. 

        Continue calibrating the "erosion", "dilation", and "canny" thresholds until you get what looks like 2 finite lines.

        The lines do not have to be perfect, just distinguishable, and there should be 0 other noise in the image.

        save your command.json and you're all set, there may be slight modifications to "max_line_gap" to get appropriate data.

    From here down is just technical specifications of the greedy algroithm that Tyler and I developed:

    Greedy Algorithm:
        This is a cheap "pixel-counting" algorithm. We start by finding the first index that is not black. Once found, we attempt to 
        see if there exists a pixel within +-max_line_gap (see command.json) pixels that is white. If we do, then we can assume there is a line here
        and we can declare this point as the start of a line.

        We then attempt to find the second starting point, it must be at minimum max_line_distance away from the first line, otherwise we will only have
        1 line and cannot compute the rest of the algorithm.

        Once both starting points are found, we attempt to find the end points by iterating in the reverse direction. and doing the same as above.

        We then combine the points and assume point A-B is a contigious line.

        From there, we count the pixel distances over these 2 contigious lines, and multiply by the ratio found in the yml file of the given camera.

        We then have an array of distances over the interval.

        An alternative method discussed was to simply return the 4 points found and let the operator calculate, however, in interest of a more loosley coupled
        system, we decided against this.

        Once found, we write to the pipe, or send the data to the console to verify in valmar-debug mode


Command.json:
    To prevent recompiling every time we want to change something, it makes sense for us to have a method to read and write from. This file is read in
    and updating during runtime in valmar package. Additionally, mars has access to the command.json (we write and read from target/command.json). 

    {
      "capture": {
        "exposure_us": 500, -------------------------------------Exposure time in Microseconds of the camrea
        "framerate": 100, ---------------------------------------Framerate of the Camera (currently does not change)
        "gain": 2,-----------------------------------------------Gain (1-3) of the camera
        "sharpness": 0.5,----------------------------------------Sharpness 0-1.0
        "gamma_y": 1.0-------------------------------------------Luminosity of the cam (0-1.0)
      },
      "calibration": {
        "coefficient_location": "/phobos/goddard/valmar/",-------Location for Valmar to look for the "yml" files generated from calibration
        "write_location": "/phobos/goddard/mars/files/",---------Location for Valmar to write pictures when it needs to send some back to the operator
        "conversion_factor": 0.1875,-----------------------------Inches of a square on the current chessboard
        "checkerboard": {
          "width": 9,--------------------------------------------Number of "Inner points" of the chessboard width (check opencv docs)
          "height": 6--------------------------------------------Number of "Inner points" of the chessboard height (same as above)
        }
      },
      "processing": {
        "frames_to_process": 10,---------------------------------Number of frames to capture of the beam gap, and calculate using greedy algorithm, keep # low for high speeds, high for low speeds
        "greedy_line_algorithm": {
          "max_line_gap": 20
        },
        "sum_threshold": 180,
        "erosion_kernel_size": {---------------------------------We do 2 erosions and dilations to reduce noise in the image, this happens first, increasing will alter noise dramatically
          "horizontal": 5,
          "vertical": 3
        },
        "dilation_kernel_size": {--------------------------------#2 increasing will cause thicker lines
          "horizontal": 1,
          "vertical": 5
        },
        "erosion_kernel_size_post": {----------------------------#3 increasing will decrease noice dramatically
          "horizontal": 25,
          "vertical": 1
        },
        "dilation_kernel_size_post": {---------------------------#4 increasing will finalize thicker lines.
          "horizontal": 1,
          "vertical": 1
        },
        "vertical_edge_thresholds": {----------------------------Canny first and second thresholds (see opencv docs)
          "canny_2": 7000,
          "canny_1": 1000
        }
      },
      "command": {
        "refresh_frame_interval": 10,----------------------------Refresh settings in command.json after x frames captured by a single camera
        "enabled": true------------------------------------------If true, valmar runs, when set to false, we stop valmar, and it will need to be restarted to continue. (launched via ./valmar)
      },
      "ximea_cameras": {
        "right": "12531150",-------------------------------------Serial ID of cameras
        "left": "15533850"---------------------------------------^
      },
      "output": "/phobos/goddard/valmar/beam.gap"----------------Where we write our distances to during mars-hookup
      "beam_img_backup": ""--------------------------------------Set on start of valmar through mars, where to write pictures of the ibeam, backup because it will be a fallback if valmar failed.
    }
