import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backend.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class MARS_PRIMARY(object):
    """
    1) RunClock,SystemVoltage
    2) RunCLock,BatteryRemaining
    3) RunClock,TotalDisplacement
    4) IBeam,TotalDisplacement
    5) SetSpeed,RPM
    6) RPM,Speed
    """
    def __init__(self, valueColor = 'blue',theoColor='red'):
        self._shape = (3,2)
        self._theoColor = theoColor
        self._valueColor = valueColor
        self._patch =  [patches.Patch(color=theoColor,label='predicted values')]

      
        #creating dictionary of lists 
        #each of which contains independent and dependent values
        self._rc = str(self._shape[0],self._shape[1])
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
        self._plt = setup_plot()
        self._fig = self._plt.gcf()
        self._canvas = FigureCanvasTkAgg(self.fig, master=self)


    def setup_plot(self)
        spID = self._subplotIDs
        # 1) RunClock,SysVoltage
        plt.subplot(spID["RunClock:SystemVoltage"])
        plt.title("Voltage over time")
        plt.xlabel("Run Time [sec]")
        plt.ylabel("System Voltage [Volts]")
        plt.legend(handles=self._patch)
        # 2) RunClock,BatteryRemaing
        plt.subplot(spID["RunClock:BatteryRemaining"])
        plt.title("Battery over time")
        plt.xlabel("Run Time [sec]")
        plt.ylabel("Battery Remaining [%%]")
        plt.legend(handles=self._patch)
        # 3) RunClock,TotalDisplacement
        plt.subplot(spID["RunClock:TotalDisplacement"])
        plt.title("Distance Down Tube")
        plt.xlabel("Run Time [sec]")
        plt.ylabel("Displacement [meters]")
        plt.legend(handles=self._patch)
        # 4) IBeam, TotalDisplacement
        plt.subplot(spID["IBeam:TotalDisplacement"])
        plt.title("distance by Ibeam")
        plt.xlabel("IBeam [count]")
        plt.ylabel("Displacement [meters]")
        plt.legend(handles=self._patch)
        # 5) SetSpeed, RPM
        plt.subplot(spID["SetSpeed:RPM"])
        plt.title("real speed vs set speed")
        plt.xlabel("programmed speed [rpm]")
        plt.ylabel("real speed [rpm]")
        plt.legend(handles=self._patch)
        # 6) RPM, Speed
        plt.subplot(spID["RPM:Speed"])
        plt.title("rpm and linear speed")
        plt.xlabel("rpm [rpm]")
        plt.ylabel("real speed [m/s]")
        plt.legend(handles=self._patch)

        return plt

    
    def graph(self,key,x,y):
        self._values[key][0].append(x)
        self._values[key][1].append(y)

        xReal = self._values[key][0]
        yReal = self._values[key][1] 
        
        self._plt.subplot(subplotIDs[key])
        self._plt.clear()
        self._plt.plot( self._values[key], color = self._valueColor )

        if key in self._theoreticals:
            theo = calc_theoretical(key,x)
            self._theoreticals[key][0].append(x)
            self._theoreticals[key][1].append(theo)

        return self._plt
    
    def clear()
        self._fig.clear()         
  
    def calc_theoretical(self,key,x):
        """
        ALL THEORETICAL VALUES MUST BE REGRESSED OR CALCULATED ONCE DAQ IS COMPLETE
        FOR NOW PLACEHOLDER IS USED
        """
        return 2 * x 


