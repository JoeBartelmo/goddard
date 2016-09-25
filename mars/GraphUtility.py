# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import numpy as np
from matplotlib import pyplot as pyp
from matplotlib.backends.backend_pdf import PdfPages
import os
import fnmatch
import logging

logger = logging.getLogger('mars_logging')
telemetryGraphName = 'telemetry_graph.pdf'

class GraphUtility(object):

    def __init__(self, config):
        self.fileLoc = config.file_forward_location
        self.output_path = config.logging.output_path + '/output'

    def get_all_outputs(self):
        if not os.path.exists(self.output_path):
            logger.warning('output folder does not exist, cannot get outputs')
            return []
        mtime = lambda f: os.stat(os.path.join(self.output_path, f)).st_mtime
        return list(sorted(os.listdir(self.output_path), key=mtime))

    def generate_pdf(self, inputFolder = None):
        if inputFolder is None:
            if len(self.get_all_outputs()) is 0:
                return
            inputFolder = self.get_all_outputs()[0]
        inputFolder = self.output_path + '/' + inputFolder

        if os.path.isdir(inputFolder) == False:
            logger.error('Attempted to load logs from directory ' + inputFolder + ' failed. Folder does not exist')
            return

        for f in os.listdir(inputFolder):
            if fnmatch.fnmatch(f, '*.csv'):
                filename = inputFolder + '/' + f
        
        if filename is None:
            log.warning('Could not find a *.csv file in ' + inputFolder)
            return
        logger.info(filename) 
        with PdfPages(telemetryGraphName) as pdf:

            out = pdf.infodict()
            out['Title'] = 'Telemetry data graphs'
            out['Author'] = 'RIT Hyperloop'
            out['Subject'] = 'Graphs of MARS telemetry data'

            invals = np.genfromtxt(filename, names=True, delimiter=',')

            def plot_data(x, y, x_label, y_label, title):
                x=invals[x]
                y=invals[y]
                pyp.plot(x, y)
                pyp.xlabel(x_label) 
                pyp.ylabel(y_label) 
                pyp.title(title)
                pdf.savefig()
                pyp.clf()
            plot_data('TotalDistance', 'BatteryRemaining', 'Total Distance', 'Battery Remaining', 'Remaining Battery versus distance traveled')
            plot_data('BatteryRemaining', 'SystemVoltage', 'Battery Remaining', 'System Voltage', 'System voltage versus remaining battery')
            plot_data('RunClock', 'TotalDisplacement', 'Run Clock', 'Total Displacement', 'Total Displacement versus time elapsed')
            plot_data('RunClock', 'Speed', 'Run Clock', 'Speed', 'Speed versus time elapsed')
            plot_data('RunClock', 'BatteryRemaining', 'Run Clock', 'Battery Remaining', 'Remaining Battery versus time elapsed')
    
            pyp.close()

            #file is now generated. Move it into folder and have the server take care of the rest
            os.rename(telemetryGraphName, self.fileLoc + telemetryGraphName)
    os.rename(telemetryGraphName, self.fileLoc + telemetryGraphName)
