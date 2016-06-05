import Tkinter as tk
import sys

class TelemetryWidget(tk.Frame):
    def __init__(self, parent):
        self.frame = tk.Frame()
        tk.Frame.__init__(self)
        self.parent = parent
        
        label1 = tk.Label(master=root, text="")
        label1.grid()
