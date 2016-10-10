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
/**
* JsonSettings is a class that deserializes the settings.json
* into an easily understood c++ class
*/
class JsonSettings {
    json settings;
    public:
        bool isEnabled();

        int getIBeamOffset();
        void setIBeamOffset(int offset);

        int getFrameRate();
        int getExposureTime();
        int getGain();
        double getGammaLuminosity();
        double getSharpness();

        int getHistogramMax();
        int getThreshold();
        
        int getRefreshInterval();
        void refreshAllData(string filename);

        int getCheckerboardWidth();
        int getCheckerboardHeight();
        double getPixelConversionFactor();

        int getHoughLineMaxGap();
        
        int getCannyThreshold(int i);
        Mat getErosionMat(int mode);
        Mat getDilationMat(int mode);

        const char* getOutputFifoLoc();
        string getCoefficientLoc();

        char* getCamera(const char* camera);
};

