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

int getScalarHistogram(const Mat& image, unsigned char upperRange) {
    int histSize[] = {256};    // bin size
    float range[] = { 0, (float)upperRange };
    const float *ranges[] = { range };
    int channels[] = {0};
    // Calculate histogram
    Mat hist;
    calcHist(&image, 1, channels, Mat(), hist, 1, histSize, ranges, true, false ); // # OF IMAGES SET TO 1, CAN CHANGE
    double histSum= sum(hist)[0];
#if DEBUG
    printf("Histogram: %f\n", histSum);
#endif
    return (int)histSum;
}

void writeToPipe(int pipe, vector<double> &array, double processingTime, int framesToProcess,
        xiAPIplusCameraOcv *leftCam/*, xiAPIplusCameraOcv *rightCam*/, 
        double displacementLeft/*, double displacementRight*/, int frameLeft
        /*, int frameRight*/) {
    json data;
    data["Enabled"] = settings.isEnabled();
    data["IbeamCounter"] = ++iBeamCounter;
    data["BeamGap"] = array;
    data["HistogramThreshold"] = settings.getHistogramMax();
    data["AvgProcessingTime"] = processingTime;
    data["FramesToProcess"] = framesToProcess;

    data["Left"]["FrameNumber"] = frameLeft;
    data["Left"]["Framerate"] = (*leftCam).GetFrameRate();
    data["Left"]["Exposure"] = (*leftCam).GetExposureTime(); 
    data["Left"]["Sharpness"] = (*leftCam).GetSharpness(); 
    data["Left"]["GammaY"] = (*leftCam).GetGammaLuminosity(); 
    data["Left"]["Gain"] = (*leftCam).GetGain();
    data["Left"]["PixelDisplacementRatio"] = displacementLeft;
    /* 
    data["Right"]["FrameNumber"] = frameRight;
    data["Right"]["Framerate"] = (*rightCam).GetFrameRate();
    data["Right"]["Exposure"] = (*rightCam).GetExposureTime(); 
    data["Right"]["Sharpness"] = (*rightCam).GetSharpness(); 
    data["Right"]["GammaY"] = (*rightCam).GetGammaLuminosity(); 
    data["Right"]["Gain"] = (*rightCam).GetGain();
    data["Right"]["PixelDisplacementRatio"] = displacementRight;
    */
    uint32_t length = (uint32_t)strlen(((string)data.dump()).c_str());
#if !DEBUG
    write(pipe, (char*)(&length), sizeof(length));
    write(pipe, ((string)data.dump()).c_str(), length);
#else
    printf("Size of %d would have been sent. along with: %s\n", (unsigned int)length, ((string)data.dump()).c_str());
#endif
    array.clear();
}

/**
* Loads in distortion coefficients
* Connects to Fifo
* while valmar is enabled
*       Finds histogram
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
    //xiAPIplusCameraOcv rightCam;

    leftCam.OpenBySN(settings.getCamera(leftCamera));
    //rightCam.OpenBySN(settings.getCamera(rightCamera));
   
    if (!checkFileExists(settings.getCoefficientLoc() + "left_calibration_coefficients.yml")/* || !checkFileExists(settings.getCoefficientLoc() + "right_calibration_coefficients.yml")*/) {
        printf("No camera calibration file found, run ./calibrate to generate calibration coefficients...\n");
        return EXIT_FAILURE;
    }
 
    //calculate maps for remapping
    assignSettings(settings, settingsFile, &leftCam);
    try {
        printf("Starting acquisition...\n");
        leftCam.StartAcquisition();
        //rightCam.startAcquisition();
    }
    catch(xiAPIplus_Exception& exp) {
        printf("Error occured on attempting to start acquisition\n");
        exp.PrintError(); // report error if some call fails
        return EXIT_FAILURE;
    }

// #################DISTORTION###################################
    Mat leftCameraMatrix, rightCameraMatrix, leftDistCoeffs, rightDistCoeffs, map1, map2, map3, map4;
    Size imageSize = leftCam.GetNextImageOcvMat().size();
    double leftConversionFactor, rightConversionFactor; 
    Rect leftCropRegion, rightCropRegion;
    
    FileStorage reader(settings.getCoefficientLoc() + "left_calibration_coefficients.yml", FileStorage::READ);
    reader["distribution_coefficients"] >> leftDistCoeffs;
    reader["camera_matrix"] >> leftCameraMatrix;
    //reader["corners"] >> imagePoints;
    reader["inches_conversion_factor"] >> leftConversionFactor;
    reader.release();

    //calculate maps for remapping
    initUndistortRectifyMap(leftCameraMatrix, leftDistCoeffs, Mat(),
            getOptimalNewCameraMatrix(leftCameraMatrix, leftDistCoeffs, imageSize, 1, imageSize, &leftCropRegion),
            imageSize, CV_16SC2, map1, map2);


    /*uncomment when right camera hooked up
    FileStorage reader(settings.getCoefficientLoc() + "right_calibration_coefficients.yml", FileStorage::READ);
    reader["distribution_coefficients"] >> rightDistCoeffs;
    reader["camera_matrix"] >> rightCameraMatrix;
    //reader["corners"] >> imagePoints;
    reader["inches_conversion_factor"] >> rightConversionFactor;
    reader.release();

    Mat right_correct_view, map3, map4;
    initUndistortRectifyMap(rightCameraMatrix, rightDistCoeffs, Mat(),
            getOptimalNewCameraMatrix(leftCameraMatrix, rightDistCoeffs, imageSize, 1, imageSize, &rightCropRegion),
            imageSize, CV_16SC2, map3, map4);
    */
// ###############################################################
    int refresh_tick = 0;
    int hist;
    vector<double> distances = vector<double>();
    vector<double> temp_distances = vector<double>();
    bool threshold_triggered = false;

    register Mat leftFrame, horizontal_left, horizontal_right, ROI;//, rightFrame;
    Mat undistortLeft, undistortRight;
    printf("Beginning valmar...\n");

    //stopwatch
    std::chrono::time_point<std::chrono::system_clock> start, end;
    //totalFrames
    int totalFrames = 0, leftFrameNumber = 0, rightFrameNumber = 0, leftCount = 0, rightCount = 0;

    while(settings.isEnabled()) {
        // getting image from camera
        try {
            leftFrame = leftCam.GetNextImageOcvMat();
            //rightFrame = rightCam.getNextImageOcvMat();
            leftCount++;
            rightCount++;
            hist = (getScalarHistogram(leftFrame, settings.getHistogramMax()));// + getScalarHistogram(rightFrame)) / 2;
            if (hist >= settings.getThreshold()) {
                if (!threshold_triggered) {
                    threshold_triggered = true;
                    start = std::chrono::system_clock::now();
                }
                totalFrames += 1;
                printf("Histogram threshold of %d reached threshold of %d\n", hist, settings.getThreshold());
                //undistortImages
                remap(leftFrame, undistortLeft, map1, map2, INTER_LINEAR); // remap using previously calculated maps
                
                ROI = Mat(undistortLeft, leftCropRegion);
                ROI.copyTo(undistortLeft);
                //remap(rightFrame, undistortRight, map3, map4, INTER_LINEAR); // remap using previously calculated maps

                //ROI(undistortLeft, leftCropRegion);
                //ROI.copyTo(undistortLeft);
                horizontal_left = retrieveHorizontalEdges(undistortLeft, settings.getCannyThreshold(1), settings.getCannyThreshold(2), 
                                        settings.getErosionMat(0), settings.getDilationMat(0), settings.getErosionMat(1), settings.getDilationMat(1));
                //horizontal_right = retrieveHorizontalEdges(undistortRight,255, settings.getHistogramMax() + 5);
                if(calculateRawDistances(horizontal_left, temp_distances, settings.getHoughLineMaxGap(), leftConversionFactor)) {
                    //succesfully calculated distances
                    if (temp_distances.size() > distances.size()) {
                        distances = temp_distances;
                        leftFrameNumber = leftCount;
                    }
                    printf("Houghline success!\n");
                }
            }
            else if(threshold_triggered) {
                threshold_triggered = false;
                end = std::chrono::system_clock::now();
                std::chrono::duration<double> elapsed_seconds = end-start;
                writeToPipe(pipe, distances, elapsed_seconds.count(), totalFrames,
                        &leftCam/*, &rightCam*/, 
                        leftConversionFactor/*, rightConversionFactor*/, leftFrameNumber
                        /*, rightFrameNumber*/);
                totalFrames = 0;
                temp_distances.clear();
            }
        }
        catch(xiAPIplus_Exception& exp){
            printf("Error:\n");
            exp.PrintError();
            cvWaitKey(200);
        }
        if (refresh_tick >= settings.getRefreshInterval()) {
            assignSettings(settings, settingsFile, &leftCam);
            refresh_tick = 0;
        }
        refresh_tick++;
    }
    
    printf("Detected enabled was set to false, stopping valmar.\n");
    leftCam.StopAcquisition();
    //rightCam.StopAcquisition();
    leftCam.Close();
    //rightCam.Close();
    printf("Done\n");
}

