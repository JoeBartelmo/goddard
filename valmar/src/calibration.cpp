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
    #define PATTERN_COLS 6
    #define PATTERN_ROWS 9
    #define CALIBRATION_ATTEMPTS 10
#endif


cv::Mat CalibrationEntity::getCalibratedMatrix() {
    return calibratedMatrix;
}

double CalibrationEntity::getCalibratedConstant() {
    return calibratedConstant;
}

double CalibrationEntity::runCalibration(xiAPIplusCameraOcv *cam, bool debug) {
    Mat startMatrix = cam->GetNextImageOcvMat();
    vector<Point2f> corners;
    vector<Point3f> obj;
    
    int numSquares = PATTERN_COLS * PATTERN_ROWS; 
    Size chessBoardSize = Size(PATTERN_COLS, PATTERN_ROWS);
    printf("[VALMAR] Attemting to find chessboard\n");
    //Attempt to grab a chessboard from the camera
    for(int attempts = 0; attempts < CALIBRATION_ATTEMPTS; attempts++) {
#if defined(DEBUG)
        imwrite("debug/calibration/attempt" + std::to_string(attempts) + ".png", startMatrix);
#endif
        if (findChessboardCorners(startMatrix, chessBoardSize, corners)) {
            break;
        }
        if (attempts == CALIBRATION_ATTEMPTS - 1) {
            printf("[VALMAR] Could not find image\n");
            return -1;
        }
        startMatrix = cam->GetNextImageOcvMat();
    }
#if defined(DEBUG)
    imwrite("debug/calibration/chessBoardImg.png", startMatrix);
#endif

    //Chessboard was found, create coordinate pair set
    for(int squareIndex = 0; squareIndex < numSquares; squareIndex++) {
        obj.push_back(Point3f(squareIndex / PATTERN_COLS, squareIndex % PATTERN_ROWS, 0.0f));
    }
    cornerSubPix(startMatrix, corners, Size(11, 11), Size(-1, -1), TermCriteria(CV_TERMCRIT_EPS | CV_TERMCRIT_ITER, 30, 0.1));
    drawChessboardCorners(startMatrix, chessBoardSize, corners, true);
    
    //Run actual calibration
    Mat intrinsicMatrix = Mat(3,3, CV_32FC1), distortionCoefficients;
    vector<Mat> rotationVectors, translationVector; 
    //calibrateCamera(
}

double CalibrationEntity::runCalibration(xiAPIplusCameraOcv *cam) {
#if defined(DEBUG)
    return runCalibration(cam, true);
#endif
    return runCalibration(cam, false);
}
 
