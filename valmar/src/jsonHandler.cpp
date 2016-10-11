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
#if !defined JSON_SETTINGS
    #define JSON_SETTINGS
    #include "jsonHandler.hpp"
    #define JSON_LOAD_ATTEMPT 10
#endif

bool JsonSettings::isEnabled() {
    return settings["command"]["enabled"];
}

int JsonSettings::getFrameRate() {
    return settings["capture"]["framerate"];
}

int JsonSettings::getExposureTime() {
    return settings["capture"]["exposure_us"];
}

int JsonSettings::getGain() {
    return settings["capture"]["gain"];
}

double JsonSettings::getGammaLuminosity() {
    return (double)settings["capture"]["gamma_y"];
}

double JsonSettings::getSharpness() {
    return settings["capture"]["sharpness"];
}

int JsonSettings::getThreshold() {
    return settings["processing"]["threshold"];
}

int JsonSettings::getHistogramMax() {
    return settings["processing"]["histogram_max"];
}

int JsonSettings::getRefreshInterval() {
    return settings["command"]["refresh_frame_interval"];
}

int JsonSettings::getCheckerboardWidth() {
    return settings["calibration"]["checkerboard"]["width"];
}

int JsonSettings::getCheckerboardHeight() {
    return settings["calibration"]["checkerboard"]["height"];
}

double JsonSettings::getPixelConversionFactor() {
    return (double)settings["calibration"]["conversion_factor"];
}

int JsonSettings::getHoughLineMaxGap() {
    return settings["processing"]["hough_line"]["max_line_gap"];
}

int JsonSettings::getCannyThreshold(int i) {
    switch(i) {
        case 1:
            return settings["processing"]["vertical_edge_thresholds"]["canny_1"];
        case 2:
            return settings["processing"]["vertical_edge_thresholds"]["canny_2"];
    }
    return -1;
}

// 0 for Pre
// 1 for Post
Mat JsonSettings::getErosionMat(int mode) {
    if (mode == 0) {
        return getStructuringElement(MORPH_RECT, Size(settings["processing"]["erosion_kernel_size"]["horizontal"], 
                                                                settings["processing"]["erosion_kernel_size"]["vertical"]));
    }
    else if(mode == 1) {
        return getStructuringElement(MORPH_RECT, Size(settings["processing"]["erosion_kernel_size_post"]["horizontal"], 
                                                                settings["processing"]["erosion_kernel_size_post"]["vertical"]));
    }
    return Mat();
}

// 0 for Pre
// 1 for Post
Mat JsonSettings::getDilationMat(int mode) {
    if (mode == 0) {
        return getStructuringElement(MORPH_RECT, Size(settings["processing"]["dilation_kernel_size"]["horizontal"], 
                                                                settings["processing"]["dilation_kernel_size"]["vertical"]));
    }
    else if(mode == 1) {
        return getStructuringElement(MORPH_RECT, Size(settings["processing"]["dilation_kernel_size_post"]["horizontal"], 
                                                                settings["processing"]["dilation_kernel_size_post"]["vertical"]));
    }
    return Mat();
}

const char* JsonSettings::getOutputFifoLoc() {
    string s = settings["output"];
    return s.c_str();
}

string JsonSettings::getCoefficientLoc() {
    return settings["calibration"]["coefficient_location"];
}

//getsCameraSerialNumber
char* JsonSettings::getCamera(const char* camera) {
    //ximeas api wants a char* not a const char* :(
    string left = settings["ximea_cameras"]["left"];
    string right = settings["ximea_cameras"]["right"];
    const char* cam;
    if (strcmp(camera, "left") == 0) {
        cam = left.c_str();
    }
    else if (strcmp(camera, "right") == 0) {
        cam = right.c_str();
    }
    char* charConversion = new char[strlen(cam) + 1];
    if (charConversion) {
        strcpy(charConversion, cam);
    }
    return charConversion; 
}

void JsonSettings::refreshAllData(string filename) {
    json temp_settings;
    int attempt;    
    for(attempt = 0; attempt < JSON_LOAD_ATTEMPT; attempt++) {
        try {
            std::ifstream t(filename);
            std::stringstream buffer;
            buffer << t.rdbuf();
            temp_settings = json::parse(buffer.str());
            break;
        } catch (int i) { cvWaitKey(200); }
        if (attempt >= JSON_LOAD_ATTEMPT -1) {
            printf("Could not load settings, inuse?\n");
            return;
        }
    }
    settings = temp_settings;
}

