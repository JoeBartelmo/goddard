#include "includes.hpp"

/**
* JsonSettings is a class that deserializes the settings.json
* into an easily understood c++ class
*/
class JsonSettings {
    private:
        bool enabled;

        //camera settings
        int framerate;
        int exposure_us;
        int gain;
        double gamma_y;
        double sharpness;
        
        int image_queue_size;

        int threshold;
        int histogramMax;

        string write_location;
        double pixel_ratio;
        int ibeam_offset;

        //Camera serial id numbers
        string left;
        string right; 

        int refresh_interval;       

        void setCameraProperties();
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

        char* getCamera(const char* camera);
};

