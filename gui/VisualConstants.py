import matplotlib.pyplot as plt
import matplotlib.patches as patches

class MARS_PRIMARY(object):
    """
    1) RunClock,SystemVoltage
    2) RunCLock,BatteryRemaining
    3) RunClock,TotalDisplacement
    4) IBeam,TotalDisplacement
    5) SetSpeed,RPM
    6) RPM,Speed
    """
    def __init__(self, figureNum, valueColor = 'blue',theoColor='red'):
        self._shape = (3,2)
        self._figureNum = figureNum
        self._theoColor = theoColor
        self._valueColor = valueColor
        self._patch =  [patches.Patch(color=theoColor,label='Predicted Values')]

      
        #creating dictionary of lists 
        #each of which contains independent and dependent values
        self._rc = str(self._shape[0]) + str(self._shape[1])
        self._subplotIDs = {"RunClock:SystemVoltage":int(self._rc+"1"),
                            "RunClock:BatteryRemaining":int(self._rc+"2"),
                            "RunClock:TotalDisplacement":int(self._rc+"3"),
                            "IBeam:TotalDisplacement":int(self._rc+"4"),
                            "SetSpeed:RPM":int(self._rc+"4"),
                            "RPM:Speed":int(self._rc+"5")
                           }
        self._values = {"RunClock:SystemVoltage":[ [],[] ],
                        "RunClock:BatteryRemaining":[ [],[] ],
                        "RunClock:TotalDisplacement":[ [],[] ],
                        "IBeam:TotalDisplacement":[ [],[] ],
                        "SetSpeed:RPM":[ [],[] ],
                        "RPM:Speed":[ [],[] ]
                       }
        self._theoreticals = {"RunClock:SystemVoltage":[ [],[] ],
                              "RunClock:BatteryRemainingg":[ [],[] ],
                              "IBeam:TotalDisplacement":[ [],[] ],
                              "SetSpeed:RPM":[ [],[] ],
                              "RPM:Speed":[ [],[] ] 
                             }
        self._numPlots = len(self._values)
        self._plt = self.setup_plot()
        self._fig = self._plt.gcf()

    def set_subplot(self, _id, title, xlabel, ylabel):
        plt.subplot(_id)
        plt.title(title, fontsize = 12)
        plt.xlabel(xlabel, fontsize=10)
        plt.ylabel(ylabel, fontsize=10)
        plt.legend(handles=self._patch)

    def setup_plot(self):
        plt.figure(self._figureNum)

        spID = self._subplotIDs
        # 1) RunClock,SysVoltage
        self.set_subplot(spID["RunClock:SystemVoltage"], "Voltage over time", "Run Time [sec]", "System Voltage [Volts]")
        # 2) RunClock,BatteryRemaing
        self.set_subplot(spID["RunClock:BatteryRemaining"], "Battery over time", "Run Time [sec]", "Battery Remaining [%]")
        # 3) RunClock,TotalDisplacement
        self.set_subplot(spID["RunClock:TotalDisplacement"], "Distance Down Tube", "Run Time [sec]", "Displacement [meters]")
        # 4) IBeam, TotalDisplacement
        self.set_subplot(spID["IBeam:TotalDisplacement"], "Distance (IBeams)", "IBeam [count]", "Displacement [meters]")
        # 5) SetSpeed, RPM
        self.set_subplot(spID["SetSpeed:RPM"], "Real Speed vs Set Speed", "Programmed Speed [rpm]", "Set Speed [rpm]")
        # 6) RPM, Speed
        self.set_subplot(spID["RPM:Speed"], "RPM vs Linear Speed", "RPM [rpm]", "Real Speed [m/s]")

        plt.tight_layout()

        return plt

    
    def graph(self,key,x,y):
        self._values[key][0].append(x)
        self._values[key][1].append(y)

        xReal = self._values[key][0]
        yReal = self._values[key][1] 
        
        self._plt.subplot(self._subplotIDs[key])
        self._plt.cla()
        self._plt.plot( self._values[key], color = self._valueColor )

        if key in self._theoreticals:
            theo = self.calc_theoretical(key,x)
            self._theoreticals[key][0].append(x)
            self._theoreticals[key][1].append(theo)

        return self._plt
    
    def clear():
        self._fig.clear()         
  
    def calc_theoretical(self,key,x):
        """
        ALL THEORETICAL VALUES MUST BE REGRESSED OR CALCULATED ONCE DAQ IS COMPLETE
        FOR NOW PLACEHOLDER IS USED
        """
        return 2 * x 


