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
#include <math.h>
#if !defined(KERNAL_SIZE)
    #define KERNAL_SIZE 5 
#endif

#if DEBUG
Mat primary_src_image = imread("fourWhiteDotsRotated.png",CV_LOAD_IMAGE_GRAYSCALE);

void displayAndSave(Mat image, String image_name){
    cout << "displaying and saving "+image_name << endl;
    cv::imwrite(image_name,image);
    imshow(image_name, image);
    cvWaitKey(1);
}
#endif

/*
* Takes a matrix and detects the 2 lines in the ibeam gap
*/
Mat retrieveHorizontalEdges(const Mat src_image, int threshold1 , int threshold2, int horizontal_size, int vertical_size) {
    register Mat working_image = src_image;
#if defined DEBUG
    displayAndSave(src_image, "original.png");
#endif
    //converting to grayscale if not already
    if (working_image.channels() == 3) {
        cvtColor(src_image, working_image, CV_BGR2GRAY);
#if defined DEBUG
        displayAndSave(working_image, "grayscale.png");     
        cout << "converted to grayscale" << endl;
#endif
    }

    //Generating edge map
    
    //applying a gaussian blue prior to sobel
    GaussianBlur( src_image, working_image, Size(3,3), 0, 0, BORDER_DEFAULT );
    Sobel( working_image, working_image, CV_16S, 0, 1, 3, 1, 0, BORDER_DEFAULT );
    working_image.convertTo(working_image, CV_8S);
#if defined DEBUG    














    displayAndSave(working_image,"edge_detected.png");
    cout << "detected edges" << endl;
#endif

    //pulling out horizontal edges 
    Mat morph_kernel = getStructuringElement(MORPH_RECT, Size(horizontal_size, vertical_size));

 //   erode(working_image, working_image, morph_kernel, Point(-1,-1));
    dilate(working_image, working_image, morph_kernel, Point(-1,-1));
    erode(working_image, working_image, morph_kernel, Point(-1,-1));

    //crop edges because ximea picks up a border (~2px)
    Mat ROI(working_image, Rect(0,5,working_image.cols,working_image.rows - 10));
    ROI.copyTo(working_image);

#if defined DEBUG
    displayAndSave(working_image, "cropped_final.png");
    cout << "cropped final" << endl;
#endif

    return working_image;
}

/*
* Calculates Integer point location from vector given an offset of y
*/
int findPoint(vector<double> line, int x){
    return ((((line[3]-line[1])/(line[2]-line[0]))*((float)x-line[0]))+line[1]);
}

/*
    Eventually two types should be implemented!
    Type 0 
        utilizes the probablistic Hough Line transform to generate the equations of two lines
        distance between the two line is calculated by subracting the two
        and multiplying by the pixel_displacement_ratio
    Type 1
        uses multiple for loops to go through the image row by row
        and subtract distances left to right
*/
int calculateRawDistances(const Mat src_image, vector<double> &distances, int rho, double theta, int threshold, int min_line_length, int max_line_break, double ratio) {
    Mat line_image(src_image.rows,src_image.cols,CV_8UC3); //matrix specifically for lines, same shape as src

    vector<Vec4i> originalLines;
#if defined DEBUG 
    cout << "About to perform Hough transform" << endl;
#endif

//    HoughLinesP(src_image, lines, rho, theta, threshold, min_line_length, max_line_break);
      HoughLinesP(src_image, originalLines, rho, theta, threshold, min_line_length, max_line_break);

    vector<int> linesXs;
    vector<int> linesYs;

    for(size_t l = 0; l < originalLines.size(); l++ ){
        linesXs.push_back(originalLines[l][0]);
        linesYs.push_back(originalLines[l][1]);
        linesXs.push_back(originalLines[l][2]);
        linesYs.push_back(originalLines[l][3]); 
    }
    double xMin, xMax;
    Point xMinLoc, xMaxLoc;
    minMaxLoc(linesXs, &xMin, &xMax, &xMinLoc, &xMaxLoc);
    //yForXmin = lines[xMinLoc][1]
    //yForXmax = lines[xMaxLoc][1]
    double yMin, yMax;
    Point yMinLoc, yMaxLoc;
    minMaxLoc(linesYs, &yMin, &yMax, &yMinLoc, &yMaxLoc);
    //xForYmin = lines[yMinLoc][0]
    //xForYmax = lines[yMaxLoc][0]
    vector<vector<double>> lines = {{xMin, yMin, xMax, yMin},{xMin, yMax, xMax, yMax}};

    //Calculating distances
    //if(lines.size() < 2) { //rejecting if there are more than two lines in this image
    //    printf("Must have at least 2 lines. Given frame had %d lines. Computation is impossible.\n", lines.size());
    //    return 0; 
    //}
    int start = lines[0][0] < lines[1][0] ? lines[1][0] : lines[0][0];
    int end = lines[0][2] < lines[1][2] ? lines[0][2] : lines[1][2];
    if(!distances.empty()) {
        distances.clear();
    }
#if defined DEBUG
    cout << "SIZE OF DISTANCES:" << distances.size() << endl;
    cout << "SIZE OF LINES:" << lines.size() << endl;
    cout << "Hough performed" << endl;
    //cout << "LINE1:" << lines[0] <<  endl;
    //cout << "LINE2:" << lines[1] <<  endl;
    cout << "START:" << start << endl;
    cout << "END:" << end << endl;
    Mat line_overlay_image;
    cvtColor(src_image,line_overlay_image,CV_GRAY2RGB);
    for(size_t i = 0; i < lines.size(); i++ ){
        vector<double> single_line = lines[i];
        line(line_overlay_image, Point(single_line[0], single_line[1]), Point(single_line[2], single_line[3]), Scalar(0,0,255), 3, CV_AA);
    }
    displayAndSave(line_overlay_image,"image_with_lines.png");

#endif 
    if(lines.size() != 2) { //rejecting if there are more than two lines in this image
        printf("Must have 2 lines. Given frame had %d lines. Computation is impossible.\n", lines.size());
        return 0; 
    }
 
    for(int col = 0; col < abs(end - start); col++){ // loops for the length of the first line 
            double pixelDistance = abs(findPoint(lines[1],col) - findPoint(lines[0],col)); 
            distances.push_back(pixelDistance * ratio);
    }
    return 1;
}

/*
int main(int argc, char const *argv[])
{
#if DEBUG
    if(! primary_src_image.data){
        cout << "Unable to read image" << endl;
        return EXIT_FAILURE;
    }

    Mat horizontal_image = retrieveHorizontalEdges(primary_src_image,225,255,5);
    Mat* distances;
    if(calculateRawDistances(horizontal_image, distances) == 0) {
        return EXIT_FAILURE;
    }
    cout << "raw_distances = " << endl << distances << endl << "end of distance matrix" << endl; 
#endif

     
    return EXIT_SUCCESS;;
}
*/

