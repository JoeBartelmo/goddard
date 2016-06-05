import Tkinter as tk
import sys

class TelemetryWidget(tk.Frame):
    def __init__(self, parent):
        self.frame = tk.Frame()
        tk.Frame.__init__(self)
        self.parent = parent

        self.labels = []        
        self.label_text = ['RunClock: %s', 'Distance: %s', 'Speed: %s', 'Power: %s', 'Battery Remaining: %s', 'Integration Time: %s', 'Connected: %s', 'RPM: %s', 'System Voltage: %s', 'System Current: %s']
        
        for _text in label_text:
            self.labels.append(tk.Label(master=root, text=_text % ' '))

        for label in self.labels:   # put them all in a row
            label.grid(self.labels.index(label) + 1, 1)
        
    def update(telemetry_list):
        for i in range(10):
            self.labels[i]['text'] = self.label_text[i] % telemetry_list[i]

