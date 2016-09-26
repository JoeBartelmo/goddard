#include <iostream>
#include <sstream>
#include <time.h>
#include <stdio.h>

#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/calib3d/calib3d.hpp>
#include <opencv2/highgui/highgui.hpp>

#include "includes.hpp"
using namespace cv;
using namespace std;

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


static double computeReprojectionErrors( const vector<vector<Point3f> >& objectPoints,
                                         const vector<vector<Point2f> >& imagePoints,
                                         const vector<Mat>& rvecs, const vector<Mat>& tvecs,
                                         const Mat& cameraMatrix , const Mat& distCoeffs,
                                         vector<float>& perViewErrors)
{
    vector<Point2f> imagePoints2;
    int i, totalPoints = 0;
    double totalErr = 0, err;
    perViewErrors.resize(objectPoints.size());

    for( i = 0; i < (int)objectPoints.size(); ++i )
    {
        projectPoints( Mat(objectPoints[i]), rvecs[i], tvecs[i], cameraMatrix,
                       distCoeffs, imagePoints2);
        err = norm(Mat(imagePoints[i]), Mat(imagePoints2), CV_L2);

        int n = (int)objectPoints[i].size();
        perViewErrors[i] = (float) std::sqrt(err*err/n);
        totalErr        += err*err;
        totalPoints     += n;
    }

    return std::sqrt(totalErr/totalPoints);
}

static void calcBoardCornerPositions(Size boardSize, float squareSize, vector<Point3f>& corners)
{
    corners.clear();

    for( int i = 0; i < boardSize.height; ++i )
        for( int j = 0; j < boardSize.width; ++j )
            corners.push_back(Point3f(float( j*squareSize ), float( i*squareSize ), 0));
}

static bool runCalibration( Size& imageSize, Mat& cameraMatrix, Mat& distCoeffs,
                            vector<vector<Point2f> > imagePoints, Size boardSize, float squareSize)
{
    // define parameters
    vector<Mat> rvecs, tvecs;
    vector<float> reprojErrs;
    double totalAvgErr = 0;
    int flag = 14;

    cameraMatrix = Mat::eye(3, 3, CV_64F);
    if( flag & CV_CALIB_FIX_ASPECT_RATIO )
        cameraMatrix.at<double>(0,0) = 1.0;

    distCoeffs = Mat::zeros(8, 1, CV_64F);

    vector<vector<Point3f> > objectPoints(1);
    calcBoardCornerPositions(boardSize, squareSize, objectPoints[0]);

    objectPoints.resize(imagePoints.size(),objectPoints[0]);

    //Find intrinsic and extrinsic camera parameters
    double rms = cv::calibrateCamera(objectPoints, imagePoints, imageSize, cameraMatrix,
                                 distCoeffs, rvecs, tvecs, flag|CV_CALIB_FIX_K4|CV_CALIB_FIX_K5);

    cout << "Re-projection error reported by calibrateCamera: "<< rms << endl;

    bool ok = checkRange(cameraMatrix) && checkRange(distCoeffs);

    totalAvgErr = computeReprojectionErrors(objectPoints, imagePoints,
                                             rvecs, tvecs, cameraMatrix, distCoeffs, reprojErrs);

    cout << "Total Average Error: "<< totalAvgErr << endl;

    return ok;
}

int main(int argc, char* argv[])
{
    //load settings
    string settingsFile = "command.json";
    switch(argc) {
        case 2:
            settingsFile = argv[1];
            //Load in all settings from command json 
            settings.refreshAllData(settingsFile);
            break;
        default:
            printf("Usage:\tcalibration [command.json]\n");
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
    Size boardSize = Size(9, 6);
    float squareSize = 50.0;
    Size imageSize;
    vector<vector<Point2f> > imagePoints;

    while(true)
    {
        Mat view;
        
        view = leftCam.GetNextImageOcvMat(); // get an image
        
        imshow("Image View", view);
        char c = (char)waitKey(30);
        if( c == 'q' || c == 'Q' )
            break;
        else if(c == 'c' || c == 'C')
        {
	    printf("Frame Grabbed\n");
            imageSize = view.size();  // Format input image.

            vector<Point2f> pointBuf;

            bool found = findChessboardCorners( view, boardSize, pointBuf,
                    CV_CALIB_CB_ADAPTIVE_THRESH | CV_CALIB_CB_FAST_CHECK | CV_CALIB_CB_NORMALIZE_IMAGE);

            if (found)
            {
		printf("Chessboard Found\n");

                //Mat viewGray;
                //cvtColor(view, viewGray, COLOR_BGR2GRAY);
                cornerSubPix( view, pointBuf, Size(11,11),
                    Size(-1,-1), TermCriteria( CV_TERMCRIT_EPS+CV_TERMCRIT_ITER, 30, 0.1 ));
                
                //drawChessboardCorners( view, s.boardSize, Mat(pointBuf), found );
                imagePoints.push_back(pointBuf);
            }
        }  
    }

    printf("Running Calibration\n");
    // do calibration
    Mat cameraMatrix, distCoeffs;

    runCalibration(imageSize, cameraMatrix, distCoeffs, imagePoints, boardSize, squareSize);

    printf("Saving Stuff\n");

    FileStorage fs("dist_coeff.yml", FileStorage::WRITE);
    fs << "Distribution Coeffiecients" << distCoeffs;

    FileStorage fs_cm("cam_mat.yml", FileStorage::WRITE);
    fs_cm << "Camera Matrix" << cameraMatrix;

    printf("Saved Stuff\n");

    leftCam.StopAcquisition();
    leftCam.Close();
    //rightCam.StopAcquisition();
    //rightCam.Close();
    return 0;
}
