#include "includes.hpp"

#if !defined VALMAR_CALIBRATION
#define VALMAR_CALIBRATION
#include "calibration.hpp"
#define PATTERN_COLS 6
#define PATTERN_ROWS 9
#define CALIBRATION_ATTEMPTS 10
#endif

//http://docs.opencv.org/2.4/doc/tutorials/highgui/video-input-psnr-ssim/video-input-psnr-ssim.html#image-similarity-psnr-and-ssim
double CalibrationEntity::getPSNR(const Mat& I2)
{
    Mat s1;
    absdiff(calibratedMatrix, I2, s1);       // |I1 - I2|
    s1.convertTo(s1, CV_32F);  // cannot make a square on 8 bits
    s1 = s1.mul(s1);           // |I1 - I2|^2

    Scalar s = sum(s1);         // sum elements per channel

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    if( sse <= 1e-10) { // for small values return zero
        return 0;
    }
    else {
        double mse = sse / (double)(calibratedMatrix.channels() * calibratedMatrix.total());
        double psnr = 10.0 * log10((255 * 255) / mse);
        return psnr;
    }
}

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
 
