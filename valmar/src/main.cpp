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

//http://docs.opencv.org/2.4/doc/tutorials/highgui/video-input-psnr-ssim/video-input-psnr-ssim.html#image-similarity-psnr-and-ssim
double getPSNR(const Mat& I1, const Mat& I2)
{
    Mat s1;
    absdiff(I1, I2, s1);       // |I1 - I2|
    s1.convertTo(s1, CV_32F);  // cannot make a square on 8 bits
    s1 = s1.mul(s1);           // |I1 - I2|^2

    Scalar s = sum(s1);        // sum elements per channel

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    if( sse <= 1e-10) { // for small values return zero
        return 0;
    }
    else {
        double mse = sse / (double)(I1.channels() * I1.total());
        double psnr = 10.0 * log10((255 * 255) / mse);
#if DEBUG
        printf("PSNR: %f\n", (float)psnr);
#endif
        return psnr;
    }
}

//We need to pass in ptr b/c stream will automatically close at end of scope otherwise
void assignSettings(string settingsFile, xiAPIplusCameraOcv *cam) {
    printf("LOLOLOL\n");
    settings.refreshAllData(settingsFile);
    printf("wtf\n");
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

void writeImgAndBin(Mat mat, string name) {
    imwrite(name + ".png", mat);
    FileStorage fs(name + ".yml", FileStorage::WRITE);
    fs << name << mat;
}

Mat getBinMat(string name) {
    Mat mat;
    FileStorage fs(name + ".yml", FileStorage::READ);
    fs[name] >> mat;
    return mat;
}

/*
* Opens up cameras, takes a photo, then kills app
* TODO: Make use calibration
*/
int takePictureThenDie(string settingsFile, string defaultImage) {
    printf("Attempting connection and to take a photo\n");
    xiAPIplusCameraOcv leftCam;
    //xiAPIplusCameraOcv rightCam;

    leftCam.OpenBySN(settings.getCamera(leftCamera));
    //rightCam.OpenBySN(settings.getCamera(rightCamera));
 
    try {
        leftCam.StartAcquisition();
        //rightCam.startAcquisition();
    }
    catch(xiAPIplus_Exception& exp) {
        printf("Error occured on attempting to start acquisition\n");
        exp.PrintError(); // report error if some call fails
        return EXIT_FAILURE;
    }

    
    assignSettings(settingsFile, &leftCam);
    Mat leftFrame = leftCam.GetNextImageOcvMat();
    //Mat rightFrame = rightCam.getNextImageOcvMat();

    writeImgAndBin(leftFrame, defaultImage + "_left");
    //writeImgAndBin(rightFrame, defaultImage + "_right");

    leftCam.StopAcquisition();
    //rightCam.StopAcquisition();
    leftCam.Close();
    //rightCam.Close();
    return EXIT_SUCCESS;
}

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
        case 3:
            settingsFile = argv[1];
    
            settings.refreshAllData(settingsFile);
            
            if (strcmp(argv[2], "-assign-psnr") == 0 || 
                strcmp(argv[2], "-assign") == 0 ||
                strcmp(argv[2], "-a") == 0) {
                printf("Assign PSNR img mode detected.\n");
                return takePictureThenDie(settingsFile, defaultImage);
            }
            break;
        default:
            printf("Usage:\tvalmar [optional settings file.json]\n");
            printf("\t\tvalmar -assign-gap: Takes photo, saves as PSNR comparable image\n");
            return EXIT_FAILURE;
    }
    string leftSide = defaultImage + "_left";
    //string rightSide = defaultImage + "_right";
    register Mat leftPsnrImage = getBinMat(leftSide);
    //register Mat rightPsnrImage = getBinMat(rightSide);

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
    double psnr;
    Mat leftFrame;
    //Mat rightFrame;
    while(settings.isEnabled()) {
        // getting image from camera
        try {
            leftFrame = leftCam.GetNextImageOcvMat();
            //rightFrame = rightCam.getNextImageOcvMat();
            psnr = getPSNR(leftFrame, leftPsnrImage);// + getPSNR(rightFrame, rightPsnrImage);
            if (psnr >= settings.getPsnrThreshold()) {
                printf("PSNR of %f reached threshold of %f\n", psnr, settings.getPsnrThreshold());
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
}
