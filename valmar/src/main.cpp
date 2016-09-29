#include "includes.hpp"
#include "measurements.cpp"
#include "util.cpp"

#if !defined(JSON_SETTINGS)
    #define JSON_SETTINGS
    #include "jsonHandler.hpp"
    #define JSON_LOAD_ATTEMPT 10
#endif

const char* leftCamera = "left";
const char* rightCamera = "right";

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

void writeToPipe(int pipe, vector<double>& distances) {
    double* array = &distances[0];
    json data = { "distances" , distances };
    const char* asChar = ((string)data.dump()).c_str();
    write(pipe, asChar, strlen(asChar));
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

#if !DEBUG
// ################ FIFO ############
    printf("Connecting to Fifo as writeonly\n");
    int pipe = open(settings.getOutputFifoLoc(), O_WRONLY);
    if (pipe < 0) {
        printf("Error ocurred while attempting to connect to Fifo\n");
        return pipe;
    }
#endif

// ##################################

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
    vector<double> distances;
    register Mat leftFrame, vertical_left, vertical_right, ROI;//, rightFrame;
    Mat undistortLeft, undistortRight;
    printf("Beginning valmar...\n");
    while(settings.isEnabled()) {
        // getting image from camera
        try {
            leftFrame = leftCam.GetNextImageOcvMat();
            //rightFrame = rightCam.getNextImageOcvMat();
            hist = (getScalarHistogram(leftFrame, settings.getHistogramMax()));// + getScalarHistogram(rightFrame)) / 2;
            if (hist >= settings.getThreshold()) {
                printf("Histogram threshold of %d reached threshold of %d\n", hist, settings.getThreshold());
                //undistortImages
                remap(leftFrame, undistortLeft, map1, map2, INTER_LINEAR); // remap using previously calculated maps
                
                ROI = Mat(undistortLeft, leftCropRegion);
                ROI.copyTo(undistortLeft);
                //remap(rightFrame, undistortRight, map3, map4, INTER_LINEAR); // remap using previously calculated maps

                //ROI(undistortLeft, leftCropRegion);
                //ROI.copyTo(undistortLeft);
                vertical_left = retrieveVerticalEdges(undistortLeft, settings.getCannyThreshold(1), settings.getCannyThreshold(2), settings.getHorizontalMorph(), settings.getVerticalMorph());
                //vertical_right = retrieveVerticalEdges(undistortRight,255, settings.getHistogramMax() + 5);
                if(calculateRawDistances(vertical_left, distances, settings.getHoughLineRho(), settings.getHoughLineTheta(),
                        settings.getHoughLineThreshold(), settings.getHoughLineMinLength(), settings.getHoughLineMaxGap(), leftConversionFactor)) {
                    //succesfully calculated distances
                    printf("Houghline success!\n");
#if !DEBUG
                    writeToPipe(pipe, distances);
#endif
                }
            }
            distances.clear();
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

