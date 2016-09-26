#include "includes.hpp"
#include "measurements.cpp"
#if !defined(JSON_SETTINGS)
    #define JSON_SETTINGS
    #include "jsonHandler.hpp"
    #define JSON_LOAD_ATTEMPT 10
#endif

#define DELTA_DOUBLE_THRESHOLD 0.00005

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

//We need to pass in ptr b/c stream will automatically close at end of scope otherwise
void assignSettings(string settingsFile, xiAPIplusCameraOcv *cam) {
    settings.refreshAllData(settingsFile);
#if DEBUG
    printf("#####################################\n");
    printf("Printing Settings of Camera currently:\n");
    printf("#####################################\n");
#endif


    if ((int)(*cam).GetExposureTime() != settings.getExposureTime()) {
#if DEBUG
        printf("\tExposure: %d\n", (int)(*cam).GetExposureTime());
#endif
        (*cam).SetExposureTime(settings.getExposureTime());
    }

    //The only one i can't seem to adjust right    
    //if ((int)(*cam).GetFrameRate() != settings.getFrameRate()) {
    //    (*cam).SetFrameRate(settings.getExposureTime());
    //}

    if ((int)(*cam).GetGain() != settings.getGain()) {
#if DEBUG
        printf("\tGain: %d\n", (int)(*cam).GetGain());
#endif
        (*cam).SetGain(settings.getGain());
    }

    if (abs((*cam).GetGammaLuminosity() - settings.getGammaLuminosity()) > DELTA_DOUBLE_THRESHOLD) {
#if DEBUG
        printf("\tGammaY: %f\n", (float)(*cam).GetGain());
#endif
        //(*cam).SetGammaLuminosity(settings.getGammaLuminosity());
    }
    
    if (abs((*cam).GetSharpness() - settings.getSharpness()) > DELTA_DOUBLE_THRESHOLD) {
#if DEBUG
        printf("\tSharpness: %f\n", (float)(*cam).GetSharpness());
#endif
        (*cam).SetSharpness(settings.getSharpness());
    }
#if DEBUG
    printf("#####################################\n");
    printf("#####################################\n");
#endif
}

/*
* Opens up cameras, takes a photo, then kills app
* TODO: Make use calibration
*/
int _tmain(int argc, _TCHAR* argv[])
{  
    //load settings
    string settingsFile = "command.json";
    string defaultImage = "psnr_img";
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

    // Retrieving a handle to the camera device
    printf("Opening first camera...\n");
    
    assignSettings(settingsFile, &leftCam);
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
 
    printf("Waiting for PSNR Trigger...\n");
 
    int refresh_tick = 0;
    int hist;
    register Mat leftFrame, distances;//, rightFrame;
    while(settings.isEnabled()) {
        // getting image from camera
        try {
            leftFrame = leftCam.GetNextImageOcvMat();
            //rightFrame = rightCam.getNextImageOcvMat();
            hist = (getScalarHistogram(leftFrame, settings.getHistogramMax()));// + getScalarHistogram(rightFrame)) / 2;
            if (hist >= settings.getThreshold()) {
                printf("Histogram threshold of %d reached threshold of %d\n", hist, settings.getThreshold());
                
                if(calculateRawDistances(leftFrame, distances)) {
                    //succesfully calculated distances
                    printf("Houghline success!\n");
                }
            }
        }
        catch(xiAPIplus_Exception& exp){
            printf("Error:\n");
            exp.PrintError();
            cvWaitKey(200);
        }
        if (refresh_tick >= settings.getRefreshInterval()) {
            assignSettings(settingsFile, &leftCam);
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

