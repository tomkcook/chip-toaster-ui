'''
Created on 14 Feb 2017

@author: tkcook
'''
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import QBasicTimer

import serial
import serial.tools.list_ports as list_ports

class MyFigure(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)
        self.axes.plot(range(5), [0]*5)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
    
    def update_figure(self, data):
        self.axes.cla()
        self.axes.hold(True)
        for series in data:
            self.axes.plot(series[0,:], series[1,:])
        self.draw()

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('oven.ui', self)
        self.canvas = MyFigure()
        self.graph_layout.addWidget(self.canvas)
        self.timer = QBasicTimer()
        self.timer.start(400, self)
        self.serial = serial.Serial(list_ports.comports()[0].device, 115200, timeout=0.1)
        self.data = None
        self.dt = 0.25
    
    def closeEvent(self, *args, **kwargs):
        self.serial.close()
    
    def draw(self):
        self.canvas.update_figure((np.array([[0,1], [0,1]])))
        
    def timerEvent(self, e):
        pass
    