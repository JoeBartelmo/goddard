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
#include "util.cpp"
#if !defined JSON_SETTINGS
    #define JSON_SETTINGS
    #include "jsonHandler.hpp"
    #define JSON_LOAD_ATTEMPT 10
#endif
const char* leftCamera = "left";
const char* rightCamera = "right";

JsonSettings* ptrSettings = new JsonSettings();
JsonSettings settings = *ptrSettings;


static double computeReprojectionErrors( const vector<vector<Point3f> >& objectPoints,
                                         const vector<vector<Point2f> >& imagePoints,
                                         const vector<Mat>& rvecs, const vector<Mat>& tvecs,
                                         const Mat& cameraMatrix , const Mat& distCoeffs,
                                         vector<float>& perViewErrors) {
    vector<Point2f> imagePoints2;
    int i, totalPoints = 0;
    double totalErr = 0, err;
    perViewErrors.resize(objectPoints.size());

    for(i = 0; i < (int)objectPoints.size(); ++i) {
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

static void calcBoardCornerPositions(Size boardSize, float squareSize, vector<Point3f>& corners) {
    corners.clear();

    for (int i = 0; i < boardSize.height; ++i) {
        for (int j = 0; j < boardSize.width; ++j) {
            corners.push_back(Point3f(float( j*squareSize ), float( i*squareSize ), 0));
        }
    }
}

static bool runCalibration( Size& imageSize, Mat& cameraMatrix, Mat& distCoeffs,
                            vector<vector<Point2f> > imagePoints, Size boardSize, float squareSize) {
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

double distance(Point2f point1, Point2f point2){
// return euclidean distance between two points
    return sqrt(pow((point2.x - point1.x), 2) + pow((point2.y - point1.y), 2));
}

double get_pixel_distance(vector<Point2f> imagePoints, Size boardSize) {
    double sum_pixel_dist = 0.0;
    int samples = 0, index1, index2;

    for (int i = 0; i < boardSize.height; ++i) {
        for (int j = 0; j < boardSize.width - 1; ++j) {
            index1 = i * boardSize.height + j;
            index2 = i * boardSize.height + (j + 1);
            sum_pixel_dist += distance(imagePoints[index1], imagePoints[index2]);
            samples++;
        }
    }

    for (int k = 0; k < boardSize.height - 1; ++k) {
        for (int l = 0; l < boardSize.width; ++l) {
            index1 = k * boardSize.height + l;
            index2 = (k + 1) * boardSize.height + l;
            sum_pixel_dist += distance(imagePoints[index1], imagePoints[index2]);
            samples++;
        }
    }

    return sum_pixel_dist / samples;
}

int main(int argc, char* argv[])
{

    xiAPIplusCameraOcv cam;
    //load settings
    string settingsFile = "command.json";
    string camera = "";
    switch(argc) {
        case 3:
            settingsFile = argv[1];
            //Load in all settings from command json
            camera = argv[2];
            if (strcmp(argv[2], leftCamera) || strcmp(argv[2], rightCamera)) {
                settings.refreshAllData(settingsFile);
                cam.OpenBySN(settings.getCamera(argv[2]));
            }
            else {
                printf("Usage:\tcalibration [command.json] [left|right]\n");
                return EXIT_FAILURE;
            }
            break;
        default:
            printf("Usage:\tcalibration [command.json] [left|right]\n");
            return EXIT_FAILURE;
    }
    // Retrieving a handle to the camera device
    
    assignSettings(settings,settingsFile, &cam);
    try {
        printf("Starting acquisition...\n");
        cam.StartAcquisition();
    }
    catch(xiAPIplus_Exception& exp) {
        printf("Error occured on attempting to start acquisition\n");
        exp.PrintError(); // report error if some call fails
        return EXIT_FAILURE;
    }

    printf("Running Calibration (Rectification)\n");
    printf("Place checkerboard in field of view.\n");
    printf("Press c; change orientation (roll, yaw, and pitch ), repeat at least 5 times.\n");
    printf("When enough samples have been taken, press q.\n");
    printf("(All these key presses need to happen with the picture window in focus \n(i.e. click on the window with the video stream in it before tying the letters.))\n");

    Size boardSize = Size(settings.getCheckerboardWidth(), settings.getCheckerboardHeight());
    float squareSize = 50;
    vector<vector<Point2f> > imagePoints;
    Mat cameraMatrix, distCoeffs;
    int refresh_tick = 0;
    char c = '\0';
    FileStorage writer;
    register Mat view = cam.GetNextImageOcvMat(); // get an image - for image size
    Size imageSize = view.size();


    bool calibrate = true;
    if (checkFileExists(settings.getCoefficientLoc() + camera + "_calibration_coefficients.yml")) {
        printf("\n\nDetected %s exists, would you like to overwrite it?\ny/N: ", (camera + "_calibration_coefficients.yml").c_str());
        char input;
        cin >> input;
        calibrate = input == 'y' || input == 'Y';
    }

    if (calibrate) {
        while(c != 'q' && c != 'Q') {
            view = cam.GetNextImageOcvMat(); // get an image
                imshow("Image View", view);
            c = (char)waitKey(30);
            if(c == 'c' || c == 'C') {
                printf("Frame Grabbed\n");
                vector<Point2f> pointBuf;
                bool found = findChessboardCorners( view, boardSize, pointBuf,
                        CV_CALIB_CB_ADAPTIVE_THRESH | CV_CALIB_CB_FAST_CHECK | CV_CALIB_CB_NORMALIZE_IMAGE);

                if (found) {
                    printf("Chessboard Found\n");
#if DEBUG
                    for(int i=0; i<pointBuf.size(); ++i)
                         cout << pointBuf[i] << " \n";
#endif 
                   //Mat viewGray;
                    //cvtColor(view, viewGray, COLOR_BGR2GRAY);
                    cornerSubPix( view, pointBuf, Size(11,11),
                        Size(-1,-1), TermCriteria( CV_TERMCRIT_EPS+CV_TERMCRIT_ITER, 30, 0.1 ));
                    
                    //drawChessboardCorners( view, s.boardSize, Mat(pointBuf), found );
                    imagePoints.push_back(pointBuf);
                }
            }  
            if (refresh_tick >= settings.getRefreshInterval()) {
                assignSettings(settings, settingsFile, &cam);
                refresh_tick = 0;
            }
            refresh_tick++;
        }
        runCalibration(imageSize, cameraMatrix, distCoeffs, imagePoints, boardSize, squareSize);
    }
    else {
        FileStorage reader(settings.getCoefficientLoc() + camera + "_calibration_coefficients.yml", FileStorage::READ);
        reader["distribution_coefficients"] >> distCoeffs;
        reader["camera_matrix"] >> cameraMatrix;
        reader.release();
    }
    
    if (!writer.isOpened()) {
        writer = FileStorage(settings.getCoefficientLoc() + camera + "_calibration_coefficients.yml", FileStorage::WRITE);
        writer << "distribution_coefficients" << distCoeffs;
        writer << "camera_matrix" << cameraMatrix;
    }

    //calculate maps for remapping
    Mat rview, map1, map2;
    initUndistortRectifyMap(cameraMatrix, distCoeffs, Mat(),
            getOptimalNewCameraMatrix(cameraMatrix, distCoeffs, imageSize, 1, imageSize, 0),
            imageSize, CV_16SC2, map1, map2);

    // SPLIT OF PIXEL DISTANCE CALIBRATION AND RECTIFICATION
    printf("Running Calibration (Pixel -> Real Distance Calculation)\n");
    printf("Place checkerboard in characteristic plane of rail, then press c. \n");
    printf("Rotate checkerboard, press c, repeat at least 5 times. \n");
    printf("When enough samples are taken, press q. \n");
    printf("(All these key presses need to happen with the picture window in focus \n(i.e. click on the window with the video stream in it before tying the letters.))\n");

    //get corners
    vector<Point2f> rectified_points;
    double average_pixel_distance = 0.0;
    int samples = 0;
    
    c = (char)waitKey(30);
    while(c != 'q' && c != 'Q') {   
        view = cam.GetNextImageOcvMat(); // get an image

        remap(view, rview, map1, map2, INTER_LINEAR); // remap using previously calculated maps

        imshow("Image View", rview);
        c = (char)waitKey(30);
        if(c == 'c' || c == 'C') {
            printf("Frame Grabbed\n");
            imageSize = rview.size();  // Format input image.

            cout << boardSize << endl;
            bool found = findChessboardCorners( rview, boardSize, rectified_points,
                CV_CALIB_CB_ADAPTIVE_THRESH | CV_CALIB_CB_FAST_CHECK | CV_CALIB_CB_NORMALIZE_IMAGE);

            if (found) {
                printf("Chessboard Found\n");
                for(int i=0; i<rectified_points.size(); ++i)
                     std::cout << rectified_points[i] << " \n";
                cornerSubPix( rview, rectified_points, Size(11,11),
                    Size(-1,-1), TermCriteria( CV_TERMCRIT_EPS+CV_TERMCRIT_ITER, 30, 0.1 ));
                
                //then calculate average pixel length of a side of the checkerboard

                average_pixel_distance += get_pixel_distance(rectified_points, boardSize);
                samples++;
            }
        }  
        if (refresh_tick >= settings.getRefreshInterval()) {
            assignSettings(settings, settingsFile, &cam);
            refresh_tick = 0;
        }
        refresh_tick++;
    }
    average_pixel_distance = average_pixel_distance / (double)samples;
    printf("Average Pixel Distance: %f\n", average_pixel_distance);

    double real_side_length = settings.getPixelConversionFactor(); // in inches

    printf("Inches Per Pixel: %f\n", real_side_length / average_pixel_distance);
    writer << "inches_conversion_factor" << real_side_length / average_pixel_distance;
    
    writer.release();
    cam.StopAcquisition();
    cam.Close();
    return 0;
}
