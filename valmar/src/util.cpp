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
#if !defined JSON_SETTINGS
    #define JSON_SETTINGS
    #include "jsonHandler.hpp"
    #define JSON_LOAD_ATTEMPT 10
#endif
#if !defined(UTIL)
#define UTIL

#define DELTA_DOUBLE_THRESHOLD 0.00005
void assignSettings(JsonSettings& settings, string settingsFile, xiAPIplusCameraOcv *cam) {
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

bool checkFileExists(const char *fileName) {
    ifstream infile(fileName);
    return infile.good();
}
#endif

