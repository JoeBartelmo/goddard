import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class MARS_PRIMARY(object):
    """
    1) RunClock,SystemVoltage
    2) RunCLock,BatteryRemaining
    3) RunClock,TotalDisplacement
    4) IBeam,TotalDisplacement
    5) SetSpeed,RPM
    6) RPM,Speed
    """
    def __init__(self, color='red'):
        self._shape = (3,2)
        self._patch =  [patches.Patch(color=self._color,label='ideal curve')]
        self._plt = setup_plot()

        self._valueIDs = { 1:("RunClock","SystemVoltage"),
                            2:("RunClock","BatteryRemaining"),
                            3:("RunClock","TotalDisplacement"),
                            4:("IBeam","TotalDisplacement"),
                            5:("SetSpeed","RPM"),
                            6:("RPM","Speed")}
        self._numPlot = len(self._valueIDs)
        self._theoreticals = {1:theoretical1,2:theoretical2,3:theoretical4,
                               4:theoretical4,5:theoretical5,6:theoretical6}

        
    def setup_plot(self)
        # 1) RunClock,SysVoltage
        plt.subplot(321)
        plt.title("Voltage over time")
        plt.xlabel("Run Time [sec]")
        plt.ylabel("System Voltage [Volts]")
        plt.legend(handles=self._patch)
        # 2) RunClock,BatteryRemaing
        plt.subplot(322)
        plt.title("Battery over time")
        plt.xlabel("Run Time [sec]")
        plt.ylabel("Battery Remaining [%%]")
        plt.legend(handles=self._patch)
        # 3) RunClock,TotalDisplacement
        plt.subplot(323)
        plt.title("Distance Down Tube")
        plt.xlabel("Run Time [sec]")
        plt.ylabel("Displacement [meters]")
        plt.legend(handles=self._patch)
        # 4) IBeam, TotalDisplacement
        plt.subplot(324)
        plt.title("distance by Ibeam")
        plt.xlabel("IBeam [count]")
        plt.ylabel("Displacement [meters]")
        plt.legend(handles=self._patch)
        # 5) SetSpeed, RPM
        plt.subplot(325)
        plt.title("real speed vs set speed")
        plt.xlabel("programmed speed [rpm]")
        plt.ylabel("real speed [rpm]")
        plt.legend(handles=self._patch)
        # 6) RPM, Speed
        plt.subplot(326)
        plt.title("rpm and linear speecd")
        plt.xlabel("rpm [rpm]")
        plt.ylabel("real speed [m/s]")
        plt.legend(handles=self._patch)

        return plt

    
    def draw(self,numID,value1,value2):
        sp = str(self._shape[0])+ str(self._shape[1]) + str(numID)
        self._plt.subplot(sp)
        ideal = self._theoreticals[numID](value1)

        self._plt.draw( (value1,value2) )
        self._plt.draw( (value1, ideal) color = self._color )
  
    def theoretical1(self,value):
        return 2 * value
    def theoretical2(self,value):
        return 2 * value
    def theoretical3(self,value):
        return 2 * value
    def theoretical4(self,value):
        return 2 * value
    def theoretical5(self,value):
        return 2 * value
    def theoretical6(self,value):
        return 2 * value
