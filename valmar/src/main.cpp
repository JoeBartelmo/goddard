/**
* Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
* 
* Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
* associated documentation files (the "Software"), to deal in the Software without restriction,
* including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
* subject to the following conditions:
* 
* The above copyright notice and this permission notice shall be included in all copies or substantial 
* portions of the Software.
* 
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
* LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
* WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/
#include "includes.hpp"
#include "measurements.cpp"
#include "util.cpp"
#include <future>
#include <thread>
#include <chrono>
#if !defined(JSON_SETTINGS)
    #define JSON_SETTINGS
    #include "jsonHandler.hpp"
    #define JSON_LOAD_ATTEMPT 10
#endif

//camera names
const char* leftCamera = "left";
const char* rightCamera = "right";
//keeps track of current ibeam
int iBeamCounter = 0;

JsonSettings* ptrSettings = new JsonSettings();
JsonSettings settings = *ptrSettings;


int getBinarySum(Mat& image) {
    threshold(image, image, 0, 255, CV_THRESH_BINARY | CV_THRESH_OTSU);
    double cvSum = (double)sum(image)[0] / ((double)image.rows * (double)image.cols);

#if DEBUG
    printf("Image Sum: %f\n", cvSum);
#endif
    return (int)cvSum;
}

void writeToPipe(int pipe, vector<double> &array, double processingTime, int framesToProcess,
        xiAPIplusCameraOcv *leftCam, xiAPIplusCameraOcv *rightCam, 
        double displacementLeft, double displacementRight, int frameLeft
        , int frameRight, string write_loc, std::array<Mat, 2> gap_image) {
    json data;
    data["Enabled"] = settings.isEnabled();
    data["IbeamCounter"] = ++iBeamCounter;
    data["BeamGap"] = array;
    data["HistogramThreshold"] = settings.getSumThreshold();
    data["AvgProcessingTime"] = processingTime;
    data["FramesToProcess"] = framesToProcess;

    data["Left"]["FrameNumber"] = frameLeft;
    data["Left"]["Framerate"] = (*leftCam).GetFrameRate();
    data["Left"]["Exposure"] = (*leftCam).GetExposureTime(); 
    data["Left"]["Sharpness"] = (*leftCam).GetSharpness(); 
    data["Left"]["GammaY"] = (*leftCam).GetGammaLuminosity(); 
    data["Left"]["Gain"] = (*leftCam).GetGain();
    data["Left"]["PixelDisplacementRatio"] = displacementLeft;
    
    data["Right"]["FrameNumber"] = frameRight;
    data["Right"]["Framerate"] = (*rightCam).GetFrameRate();
    data["Right"]["Exposure"] = (*rightCam).GetExposureTime(); 
    data["Right"]["Sharpness"] = (*rightCam).GetSharpness(); 
    data["Right"]["GammaY"] = (*rightCam).GetGammaLuminosity(); 
    data["Right"]["Gain"] = (*rightCam).GetGain();
    data["Right"]["PixelDisplacementRatio"] = displacementRight;
    
    uint32_t length = (uint32_t)strlen(((string)data.dump()).c_str());
#if !DEBUG
    write(pipe, (char*)(&length), sizeof(length));
    write(pipe, ((string)data.dump()).c_str(), length);
#else
    printf("Size of %d would have been sent. along with: %s\n", (unsigned int)length, ((string)data.dump()).c_str());
#endif

    //we dont want to concatenate the two images because we want to unload
    imwrite(write_loc + to_string(iBeamCounter) + "_left", gap_image[0]);
    imwrite(write_loc + to_string(iBeamCounter) + "_right", gap_image[1]);
    array.clear();
}

void assignVariables(string loc, Mat &dist, Mat &camera, double *conversionFactor) {
    FileStorage reader(loc, FileStorage::READ);
    reader["distribution_coefficients"] >> dist;
    reader["camera_matrix"] >> camera;
    //reader["corners"] >> imagePoints;
    reader["inches_conversion_factor"] >> *conversionFactor;
    reader.release();
}

/**
* Loads in distortion coefficients
* Connects to Fifo
* while valmar is enabled
*       Finds image sum
*               if threshold is met
*                       run hough line transform
*                       find distances, and report to fifo
*/
int _tmain(int argc, _TCHAR* argv[]) {  
    //load settings
    string settingsFile = "command.json";
    switch(argc) {
        case 2:
            settingsFile = argv[1];
            //Load in all settings from command json 
            settings.refreshAllData(settingsFile);
            break;
        default:
            printf("Usage:\tvalmar [command.json]\n");
            return EXIT_FAILURE;
    }

#if !DEBUG
// ################ FIFO ############
    printf("Connecting to Fifo as writeonly\n");
    int pipe = open(settings.getOutputFifoLoc(), O_WRONLY);
    if (pipe < 0) {
        printf("Error ocurred while attempting to connect to Fifo\n");
        return pipe;
    }
#else 
    int pipe = 0;
#endif

// ##################################
// ############### CAPTURE CAMERAS #############
    xiAPIplusCameraOcv leftCam;
    xiAPIplusCameraOcv rightCam;

    leftCam.OpenBySN(settings.getCamera(leftCamera));
    rightCam.OpenBySN(settings.getCamera(rightCamera));
   
    if (!checkFileExists(settings.getCoefficientLoc() + "left_calibration_coefficients.yml") || !checkFileExists(settings.getCoefficientLoc() + "right_calibration_coefficients.yml")) {
        printf("No camera calibration file found, run ./calibrate to generate calibration coefficients...\n");
        return EXIT_FAILURE;
    }
 
    //calculate maps for remapping
    assignSettings(settings, settingsFile, &leftCam);
    assignSettings(settings, settingsFile, &rightCam);
    try {
        leftCam.StartAcquisition();
        rightCam.StartAcquisition();
    }
    catch(xiAPIplus_Exception& exp) {
        printf("Error occured on attempting to start acquisition\n");
        exp.PrintError(); // report error if some call fails
        return EXIT_FAILURE;
    }

// #################DISTORTION + CALIBRATION RATIO###################################
    Mat leftCameraMatrix, rightCameraMatrix, leftDistCoeffs, rightDistCoeffs, map1, map2, map3, map4;
    Size imageSize = leftCam.GetNextImageOcvMat().size();
    double leftConversionFactor, rightConversionFactor; 
    Rect leftCropRegion, rightCropRegion;
    
    assignVariables(settings.getCoefficientLoc() + "left_calibration_coefficients.yml", leftDistCoeffs, leftCameraMatrix, &leftConversionFactor);
    assignVariables(settings.getCoefficientLoc() + "right_calibration_coefficients.yml", rightDistCoeffs, rightCameraMatrix, &rightConversionFactor);
    cout << leftDistCoeffs << endl << rightDistCoeffs << endl;
    cout << leftCameraMatrix << endl << rightCameraMatrix << endl;
    cout << leftConversionFactor << endl << rightConversionFactor << endl;
    //calculate maps for remapping
    initUndistortRectifyMap(leftCameraMatrix, leftDistCoeffs, Mat(),
            getOptimalNewCameraMatrix(leftCameraMatrix, leftDistCoeffs, imageSize, 1, imageSize, &leftCropRegion),
            imageSize, CV_16SC2, map1, map2);

    initUndistortRectifyMap(rightCameraMatrix, rightDistCoeffs, Mat(),
            getOptimalNewCameraMatrix(rightCameraMatrix, rightDistCoeffs, imageSize, 1, imageSize, &rightCropRegion),
            imageSize, CV_16SC2, map3, map4);
// ###############################################################
    int refresh_tick = 0, imgSum,
        leftCount = 0, rightCount = 0, totalFrames = 0,  rightFrameNumber = 0, leftFrameNumber = 0;
    bool threshold_triggered = false;

    printf("Beginning valmar...\n");

    //stopwatch
    std::chrono::time_point<std::chrono::system_clock> start, end;
    //totalFrames

    vector<future<vector<double>>> promises_distances;
    vector<array<Mat, 2>> gap_images;

    while(settings.isEnabled()) {
        // getting image from camera
        try {
            Mat leftFrame = leftCam.GetNextImageOcvMat();
            Mat rightFrame = rightCam.GetNextImageOcvMat();
            leftCount++;
            rightCount++;
            //we only need to do histogram for one side
            imgSum = getBinarySum(leftFrame);
            if (imgSum <= settings.getSumThreshold() && totalFrames < settings.getFramesToProcess()) {
                //start our capturing subroutine
                if (!threshold_triggered) {
                    threshold_triggered = true;
                    start = std::chrono::system_clock::now();
                }
                Mat undistortLeft, undistortRight;
                totalFrames += 1;
                printf("Sum threshold of %d reached threshold of %d\n", imgSum, settings.getSumThreshold());
                //undistortImages, we do it here as a time save (even if negligible, we want to be safe)
                remap(leftFrame, undistortLeft, map1, map2, INTER_LINEAR); // remap using previously calculated maps
                Mat ROI = Mat(undistortLeft, leftCropRegion);
                ROI.copyTo(undistortLeft);

                remap(rightFrame, undistortRight, map3, map4, INTER_LINEAR); // remap using previously calculated maps
                ROI = Mat(undistortRight, rightCropRegion);
                ROI.copyTo(undistortRight);
                
                //push our caluclation into a promise so we can keep capturing frames of the gap
                promises_distances.push_back(async(compoundCalcHorizontalDistances,undistortLeft, undistortRight, settings.getCannyThreshold(1), 
                    settings.getCannyThreshold(2), settings.getErosionMat(0), settings.getDilationMat(0), settings.getErosionMat(0), 
                    settings.getDilationMat(1), settings.getLineMaxGap(), leftConversionFactor));

                //as a backup incase valmar cant get correct data, we save the images
		//gap_images.push_back([undistortLeft, undistortRight])
            }
            else if(imgSum > settings.getSumThreshold() && threshold_triggered) {
                //end capturing subroutine
                threshold_triggered = false;
                end = std::chrono::system_clock::now();
                std::chrono::duration<double> elapsed_seconds = end-start;

                vector<double> distances;
                int railIndex;
                //among all we need to get largest size, painful if none of the promises have started
                for (int promise = 0; promise < promises_distances.size(); promise++) {
                    vector<double> curPromise = promises_distances[promise].get();
                    if (distances.size() < curPromise.size()) {
                        distances = curPromise;
                        railIndex = promise;
                    }
                }
                promises_distances.clear();

                writeToPipe(pipe, distances, elapsed_seconds.count(), totalFrames,
                        &leftCam, &rightCam, 
                        leftConversionFactor, rightConversionFactor, leftFrameNumber
                        , rightFrameNumber, settings.getBeamImgLoc(), gap_images[railIndex]);
                totalFrames = 0;
                gap_images.clear();
            }
	//we are still looking at the gap, but we have already capped our max number of frames to get from the gap
	//if this were the case, we really just do nothing, because we probably already have our data
        }
        catch(xiAPIplus_Exception& exp){
            printf("Error:\n");
            exp.PrintError();
            cvWaitKey(200);
        }
        //update settings every x ticks
        if (refresh_tick >= settings.getRefreshInterval()) {
            assignSettings(settings, settingsFile, &leftCam);
            assignSettings(settings, settingsFile, &rightCam);
            refresh_tick = 0;
        }
        refresh_tick++;
    }
    
    printf("Detected enabled was set to false, stopping valmar.\n");
    leftCam.StopAcquisition();
    rightCam.StopAcquisition();
    leftCam.Close();
    rightCam.Close();
    printf("Done\n");
}

