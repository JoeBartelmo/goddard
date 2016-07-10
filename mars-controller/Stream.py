import logging
import subprocess

class Stream (object):

    def __init__(self, config, timestamp):
        self._config = config
        self._bitrate = 'None yet'
        self._resolution = 'None yet'
        self._timestamp = timestamp
        self._init = False
        self._indexPath = self._config.logging.indexPath
        self._logPath = self._config.logging.outputPath + '/output/' + self._timestamp +'/' + self._config.logging.logName


    def refresh(self):
        """
        Refresh the stream via bash using the updated parameters
        :return:
        """
        if (self._init):
            self.close()
        logging.info('re-initializing steam with new inputs')
        newCall = 'nohup' + ' node '+ self._indexPath + ' -w '  + self._resolution[0] + ' -h ' + self._resolution[1] + ' -b ' \
                  + str(self._bitrate) + ' -f ' + self._logPath + ' &'
        logging.info(newCall)

        subprocess.call([newCall], shell=True)


        #p = subprocess.Popen(["node" , self._indexPath , "-w", self._resolution[0], "-h", self._resolution[1], "-b", str(self._bitrate), "-f", self._logPath], shell=True)


    def issue(self, myCode):
        """
        Update the bitrate and resolution given the code from terminal and then refresh the stream
        :param myCode:
        :return:
        """
        #update bitrate
        self._bitrate = int(myCode._bitrate) * 1000 #converting Mb/s to Kb/s

        #update res 640x480
        if int(myCode._code[1]) == 0:

            logging.info('re-initializing steam with new inputs')
            self._resolution = ['640', '480']

        #update res 1280x960
        elif int(myCode._code[1]) == 1:

            logging.info('re-initializing steam with new inputs')
            self._resolution = ['1280', '960']

        #Refresh stream
        self.refresh()


    def open(self):
        """
        Open stream with default parameters
        :return:
        """
        self._resolution = ['640', '480']
        self._bitrate = 4000
        self.refresh()
        self._init = True

    def close(self):
        """
        Close the stream
        :return:
        """
        if (self._init):
            logging.info('closing stream')
            subprocess.call(["node " + self._indexPath + " --close"], shell=True)
            self._init = False
        else:
            print("Stream not running")
            logging.info("Stream not running")