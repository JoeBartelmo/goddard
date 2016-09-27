CXX=g++
MAIN_SOURCES=src/xiApiPlusOcv.cpp
MAIN_SOURCES+=src/jsonHandler.cpp
#Histogram version
HIST_SOURCES=src/measurements.cpp
HIST_SOURCES=src/main.cpp
HIST_SOURCES+=$(MAIN_SOURCES)
#calibration of camera
CALIB_SOURCES=src/camera_calibration.cpp
CALIB_SOURCES+=$(MAIN_SOURCES)

MAIN_OBJECTS=$(MAIN_SOURCES:.cpp=.o)
PROGRAM=valmar
CALIB=calibrate

all: $(PROGRAM)

$(PROGRAM): $(MAIN_SOURCES)
	$(CXX) $(HIST_SOURCES) -o target/$(PROGRAM) -lm3api -std=c++11 -lopencv_core -lopencv_calib3d -lopencv_features2d -lopencv_highgui -lopencv_imgproc -L/usr/local/lib
	$(CXX) $(HIST_SOURCES) -o target/$(PROGRAM)-debug -lm3api -std=c++11 -lopencv_core -lopencv_calib3d -lopencv_features2d -lopencv_highgui -lopencv_imgproc -L/usr/local/lib -D DEBUG
	$(CXX) $(CALIB_SOURCES) -o target/$(CALIB) -lm3api -std=c++11 -lopencv_core -lopencv_calib3d -lopencv_features2d -lopencv_highgui -lopencv_imgproc -L/usr/local/lib
	$(CXX) $(CALIB_SOURCES) -o target/$(CALIB)-debug -lm3api -std=c++11 -lopencv_core -lopencv_calib3d -lopencv_features2d -lopencv_highgui -lopencv_imgproc -L/usr/local/lib -D DEBUG

$(CALIB): $(MAIN_SOURCES)
	$(CXX) $(CALIB_SOURCES) -o target/$(CALIB) -lm3api -std=c++11 -lopencv_core -lopencv_calib3d -lopencv_features2d -lopencv_highgui -lopencv_imgproc -L/usr/local/lib
	$(CXX) $(CALIB_SOURCES) -o target/$(CALIB)-debug -lm3api -std=c++11 -lopencv_core -lopencv_calib3d -lopencv_features2d -lopencv_highgui -lopencv_imgproc -L/usr/local/lib -D DEBUG
	
.cpp.o: $(patsubst %.cpp,%.o,$(wildcard *.cpp))
	$(CXX) -g -c $< -o $@

clean:
	rm -f $(PROGRAM) $(MAIN_OBJECTS)


