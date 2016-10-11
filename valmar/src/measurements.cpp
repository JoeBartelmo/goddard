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
    //cout << "displaying and saving "+image_name << endl;
    cv::imwrite(image_name,image);
    imshow(image_name, image);
    cvWaitKey(1);
}
#endif

/*
* Takes a matrix and detects the 2 lines in the ibeam gap
*/
Mat retrieveHorizontalEdges(const Mat src_image, int threshold1 , int threshold2, Mat erode_kernel, Mat dilate_kernel, Mat erode_kernel_post, Mat dilate_kernel_post) {
    register Mat working_image = src_image;
#if defined DEBUG
    displayAndSave(src_image, "original.png");
#endif
    //converting to grayscale if not already
    if (working_image.channels() == 3) {
        cvtColor(src_image, working_image, CV_BGR2GRAY);
#if defined DEBUG
        displayAndSave(working_image, "grayscale.png");     
        //cout << "converted to grayscale" << endl;
#endif
    }

    //Generating edge map
    Canny(working_image, working_image, threshold1, threshold2, KERNAL_SIZE);
    //applying a gaussian blue prior to sobel
  //  GaussianBlur( src_image, working_image, Size(3,3), 0, 0, BORDER_DEFAULT );
//    Sobel( working_image, working_image, CV_16S, 0, 1, CV_SCHARR, 1, 0, BORDER_DEFAULT );
#if defined DEBUG    
    displayAndSave(working_image,"edge_detected.png");
    //cout << "detected edges" << endl;
#endif

    dilate(working_image, working_image, dilate_kernel, Point(-1,-1));
    erode(working_image, working_image, erode_kernel, Point(-1,-1));

    dilate(working_image, working_image, dilate_kernel_post, Point(-1,-1)); 
    erode(working_image, working_image, erode_kernel_post, Point(-1,-1)); 


    //crop edges because ximea picks up a border (~2px)
    Mat ROI(working_image, Rect(0,5,working_image.cols,working_image.rows - 10));
    ROI.copyTo(working_image);

#if defined DEBUG
    displayAndSave(working_image, "cropped_final.png");
    //cout << "morphed final" << endl;
#endif

    return working_image;
}

/*
* Calculates Integer point location from vector given an offset of y
*/
int findPoint(int *line, int col){
    return (((((float)line[3]-(float)line[1])/((float)line[2]-(float)line[0]))*((float)col-(float)line[0]))+(float)line[1]);
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
int calculateRawDistances(Mat src_image, vector<double> &distances, int max_line_break, double ratio) {
    src_image.convertTo(src_image, CV_8UC3);
    Mat line_image(src_image.rows,src_image.cols,CV_8UC3); //matrix specifically for lines, same shape as src


    //lines in startX, startY, endX, endY order
    int lines[2][4] = { {-1, -1, -1, -1}, {-1, -1, -1, -1}};

    //find starting coordinates
    //for this we iterate over only half the image so we don't get a false positive
    for (size_t c = 0; c < src_image.cols / 2 && (lines[0][0] == -1 || lines[1][0] == -1); c++ ){
        for(size_t r = 0; r < src_image.rows; r++ ){
             if(src_image.at<uchar>(r,c) != 0) {
                 if(lines[0][0] == -1){
                     lines[0][0] = c;
                     lines[0][1] = r;
                 }
                 //we do need to make sure they are a reasonable distance apart to deem them as lines.
                 else if(abs(lines[0][1] - (int)r) >= max_line_break) {
                    lines[1][0] = c;
                    lines[1][1] = r;
                    break;
                 }
             }
         }
     } 

    if (lines[0][0] == -1 || lines[1][0] == -1) {
        printf("Could not find 2 distinct lines\n");
        return -1;
    }

    /*
        So now that we have a start point, we need to keep track of potential endpoints
        We don't want our two lines to get switched, we also need to know which of the 
        two lines is the lower line, and which is the upper line.
    */
    int potentialForTop[2] = {-1, -1};//y-coordinate
    int line1OnTop = lines[0][1] < lines[1][1];
    // End Coordinates - we want to iterate utnil
    for(size_t c = (src_image.cols - 1); c >= src_image.cols / 2 && (lines[0][3] == -1 || lines[1][3] == -1); c--){
        for(size_t r = 0; r < src_image.rows; r++){
            if(src_image.at<uchar>(r,c) != 0) {
                //remember we don't know which ones on top, and i don't want to decide here
                if(lines[0][3] == -1 && lines[1][3] == -1) {
                    if (potentialForTop[0] == -1) {
                        potentialForTop[0] = c;
                        potentialForTop[1] = r;
                    }
                    //now that we have a potential, we need to see a distance of at least max_line_break before we know for sure
                    else if (abs(potentialForTop[1] - (int)r) >= max_line_break) {
                        //now we may assign both, we have both coordinates
                        //note: there is an easier way to display this with boolean logic
                        //      but I felt it was more explicit and readable to display as such
                        int isPotentialOnTop = potentialForTop[1] < r;
                        if (line1OnTop) {
                            lines[0][2] = isPotentialOnTop ? potentialForTop[0] : c;
                            lines[0][3] = isPotentialOnTop ? potentialForTop[1] : r;
                            lines[1][2] = isPotentialOnTop ? c : potentialForTop[0];
                            lines[1][3] = isPotentialOnTop ? r : potentialForTop[1];
                        }
                        else {
                            lines[1][2] = isPotentialOnTop ? potentialForTop[0] : c;
                            lines[1][3] = isPotentialOnTop ? potentialForTop[1] : r;
                            lines[0][2] = isPotentialOnTop ? c : potentialForTop[0];
                            lines[0][3] = isPotentialOnTop ? r : potentialForTop[1];
                        }
                        break;
                   }
               }
           }
        }
    }

    int start = lines[0][0] < lines[1][0] ? lines[1][0] : lines[0][0];
    int end = lines[0][2] < lines[1][2] ? lines[0][2] : lines[1][2];
    if(!distances.empty()) {
        distances.clear();
    }
#if defined DEBUG
    cout << "SIZE OF DISTANCES:" << distances.size() << endl;
    cout << "Hough performed" << endl;
    //cout << "LINE1:" << lines[0] <<  endl;
    //cout << "LINE2:" << lines[1] <<  endl;
    cout << "START:" << start << endl;
    cout << "END:" << end << endl;
    Mat line_overlay_image;
    cvtColor(src_image,line_overlay_image,CV_GRAY2RGB);
    for(size_t i = 0; i < 2; i++ ){
        line(line_overlay_image, Point(lines[i][0], lines[i][1]), Point(lines[i][2], lines[i][3]), Scalar(0,0,255), 3, CV_AA);
    }
    displayAndSave(line_overlay_image,"image_with_lines.png");

#endif 
 
    for(int col = 0; col < abs(end - start); col++){ // loops for the length of the first line 
            int pixelDistance = abs(findPoint(lines[1],col) - findPoint(lines[0],col));
            distances.push_back((double)pixelDistance * ratio);
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

    Mat horizontal_image = retrieveHorizontalEdges(primary_src_image,225,255,5,2,2,2,2,14,30,15);
    vector<double> distances;
    if(calculateRawDistances(horizontal_image, distances, 2.0) == 0) {
        return EXIT_FAILURE;
    }
    cout << "raw_distances = " << endl << distances << endl << "end of distance matrix" << endl; 
#endif

     
    return EXIT_SUCCESS;;
}

*/
