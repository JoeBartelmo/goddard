#include "includes.hpp"

#if !defined(JSON_SETTINGS)
    #define JSON_SETTINGS
    #include "jsonHandler.hpp"
    #define JSON_LOAD_ATTEMPT 10
#endif

#if !defined(DELTA_DOUBLE_THRESHOLD)
    #define DELTA_DOUBLE_THRESHOLD 0.05
#endif

CalibrationEntity* ptrCalibrationEntity = new CalibrationEntity();
CalibrationEntity calibrationEntity = *ptrCalibrationEntity;

JsonSettings* ptrSettings = new JsonSettings();
JsonSettings settings = *ptrSettings;

//We need to pass in ptr b/c stream will automatically close at end of scope otherwise
void assignSettings(string settingsFile, xiAPIplusCameraOcv *cam) {
    settings.refreshAllData(settingsFile);

    if ((int)(*cam).GetExposureTime() != settings.getExposureTime()) {
        (*cam).SetExposureTime(settings.getExposureTime());
    }

    //The only one i can't seem to adjust right    
    //if ((int)(*cam).GetFrameRate() != settings.getFrameRate()) {
    //    (*cam).SetFrameRate(settings.getExposureTime());
    //}

    if ((int)(*cam).GetGain() != settings.getGain()) {
        (*cam).SetGain(settings.getGain());
    }

    if (abs((*cam).GetGammaLuminosity() - settings.getGammaLuminosity()) > DELTA_DOUBLE_THRESHOLD) {
        (*cam).SetGammaLuminosity(settings.getGammaLuminosity());
    }
    
    if (abs((*cam).GetSharpness() - settings.getSharpness()) > DELTA_DOUBLE_THRESHOLD) {
        (*cam).SetSharpness(settings.getSharpness());
    }
}

int _tmain(int argc, _TCHAR* argv[])
{  
    //load settings
    string settingsFile = "command.json";
    switch(argc) {
        case 1:
            break;
        case 2:
            settingsFile = argv[1];
            break;
        default:
            printf("Usage: capturePipe [optional settings file.json]%d\n", argc);
            return EXIT_FAILURE;
    }
    
    //Load in all settings from command json
    settings.refreshAllData(settingsFile);
    
    xiAPIplusCameraOcv leftCam;
    xiAPIplusCameraOcv rightCam;

    leftCam.OpenBySN(settings.getCamera("left"));
    //rightCam.OpenBySN(settings.getCamera("right"));

    // Retrieving a handle to the camera device
    printf("Opening first camera...\n");
    
    assignSettings(settingsFile, &cam);
    try {
        printf("Starting acquisition...\n");
        leftCam.StartAcquisition();
        //rightCam.startAcquisition();
    }
    catch(xiAPIplus_Exception& exp) {
        cout << "Error occured on attempting to start acquisition" << endl;
        exp.PrintError(); // report error if some call fails
        return EXIT_FAILURE;
    }
    printf("Running calibration cycle...\n");
    if (abs(calibrationEntity.runCalibration(&leftCamera) - (-1)) <= DELTA_DOUBLE_THRESHOLD) { 
        cam.StopAcquisition();
        cam.Close();
        printf("[VALMAR] Could not run calibration, reason listed above, terminating valmar.\n");
        return EXIT_FAILURE;
    }
 
    printf("Waiting for PSNR Trigger...\n");
    while(1) {
        if (settings.isEnabled()) {
            // getting image from camera
            try {
                const Mat frame = cam.GetNextImageOcvMat();
                
                double psnr;
                if ((psnr = calibrationEntity.getPSNR(frame)) >= settings.getPsnrThreshold()) {
                    printf("PSNR of %f reached threshold of %f\n", psnr, settings.getPsnrThreshold());
                }
            }
            catch(xiAPIplus_Exception& exp){
                printf("Error:\n");
                exp.PrintError();
                cvWaitKey(200);
            }
        }
        //assignSettings(settingsFile, &cam);
    }
    
    printf("Detected enabled was set to false, stopping valmar.\n");
    cam.StopAcquisition();
    cam.Close();
    printf("Done\n");
}

