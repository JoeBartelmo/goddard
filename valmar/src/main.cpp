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

#if !defined(VALMAR_CALIBRATION)
#define VALMAR_CALIBRATION
#include "calibration.hpp"
#endif

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
            printf("Usage: capturePipe [optional settings file.json]%d", argc);
            return EXIT_FAILURE;
    }
    
    // Sample for XIMEA OpenCV
    xiAPIplusCameraOcv cam;

    // Retrieving a handle to the camera device
    printf("Opening first camera...\n");
    cam.OpenFirst();
    
    assignSettings(settingsFile, &cam);

    printf("Starting acquisition...\n");
    cam.StartAcquisition();
   
    printf("Running calibration cycle...\n");
    if (abs(calibrationEntity.runCalibration(&cam) - (-1)) <= DELTA_DOUBLE_THRESHOLD) { 
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

