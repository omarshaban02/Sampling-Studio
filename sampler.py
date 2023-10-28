import numpy as np
import pyqtgraph as pg
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from scipy import signal

class AbstractSignal(object):
  def __init__(self):

    self._signal_plot = None
    self._resampled_signal_plot = None
    self._resampling_data = None
    self._SNR = None
    self._resampling_freq = None
    self._difference_signal_plot = None
    self._recovered_signal_plot = None
    self._time_range = (0, 1)
    self.space_length = 1000
    self.linspace = np.linspace(self.time_range[0],self.time_range[1],self.space_length,endpoint=False)
    self._signal = None
    self.noise_values = None
    


  
  @property
  def time_range(self):
    return self._time_range
  @time_range.setter
  def time_range(self,value):
    self._time_range = value

  @property
  def signal_plot(self):
    return self._signal_plot
  @signal_plot.setter
  def signal_plot(self,value):
    self._signal_plot = value

  @property
  def resampled_signal_plot(self):
    number_of_samples = self.resampling_freq * (self.time_range[1]-self.time_range[0])
    self.resampling_data = signal.resample(self.signal,num = number_of_samples)
    xnew = np.linspace(self.time_range[0], self.time_range[1],number_of_samples,endpoint =False)
    plt = pg.ScatterPlotItem(xnew, self.resampling_data)
    self.resampled_signal_plot = plt
    return self._resampled_signal_plot
  @resampled_signal_plot.setter
  def resampled_signal_plot(self,value):
    self._resampled_signal_plot=value

  @property
  def resampling_data(self):
    number_of_samples = self.resampling_freq * (self.time_range[1]-self.time_range[0])
    self.resampling_data = signal.resample(self.signal,num = number_of_samples)
    return self._resampling_data
  @resampling_data.setter
  def resampling_data(self,value):
    self._resampling_data=value

  @property
  def SNR(self):
    return self._SNR
  @SNR.setter
  def SNR(self,value):
    self._SNR=value
    random_numbers  = np.random.normal(0,0.1,self.space_length)
    alpha = np.sqrt(self._SNR * (np.sum(np.square(random_numbers))/np.sum(np.square(np.asarray(self.signal)))))
    self.noise_values = alpha * random_numbers
    
  @property
  def resampling_freq(self):
    return self._resampling_freq
  @resampling_freq.setter
  def resampling_freq(self,value):
    self._resampling_freq=value

  @property
  def difference_signal_plot(self):
    recovered_signal = np.asarray(self.sinc_interpolation(self.resampling_data,self.sampling_freq, self.linspace))
    original_signal = np.asarray(self.signal)
    plt = pg.PlotDataItem(self.linspace, original_signal-recovered_signal)
    self.difference_signal_plot = plt
    return self._difference_signal_plot
  
  @difference_signal_plot.setter
  def difference_signal_plot(self,value):
    self._difference_signal_plot=value

  @property
  def recovered_signal_plot(self):
    signal = np.asarray(self.sinc_interpolation(self.resampling_data,self.sampling_freq, self.linspace))+self.noise_values
    plt = pg.PlotDataItem(self.linspace, signal)
    self.recovered_signal_plot=plt
    return self._recovered_signal_plot
  @recovered_signal_plot.setter
  def recovered_signal_plot(self,value):
    self._recovered_signal_plot=value

  @property
  def signal(self):
    return self._signal
  @signal.setter
  def signal(self,value):
    self._signal=value



  def sinc_interpolation(self, sampled_signal, sampling_frequency, linspace):
    # sampling period
    T = 1 / (sampling_frequency)
    # number of samples
    N = len(sampled_signal)
    time_samples = np.arange(0,N*T,T)
    sinc = lambda t: np.sum(np.dot(sampled_signal,np.sinc((t-time_samples)/T)))
    recovered_signal = list(map(sinc, linspace))
    return recovered_signal




class Signal(AbstractSignal):
  def __init__(self, data: np.ndarray):
    super().__init__()
    self._data = data
    self._sampling_freq = 125
    self._samples_number = len(data)
    
    self._sampling_period = 1/125
    
    
  @property
  def signal(self):
    signal = self.sinc_interpolation(self.data,self.sampling_freq, self.linspace)
    self._signal = signal
    return self._signal
  @signal.setter
  def signal(self,value):
    
    self._signal=value   


  @property
  def data(self):
    return self._data
  @data.setter
  def data(self,value):
    self._data = value

  @property
  def sampling_freq(self):
    return self._sampling_freq
  @sampling_freq.setter
  def sampling_freq(self,value):
    self._sampling_freq = value

  @property
  def samples_number(self):
    return self._samples_number
  @samples_number.setter
  def samples_number(self,value):
    self._samples_number = value

  @property
  def sampling_period(self):
    return self._sampling_period
  @sampling_period.setter
  def sampling_period(self,value):
    self._sampling_period=value

  @property
  def signal_plot(self):
    signal = np.asarray(self.sinc_interpolation(self.data,self.sampling_freq, self.linspace))+self.noise_values
    plot = pg.PlotDataItem(self.linspace, signal)
    self._signal_plot = plot
    return self._signal_plot
  @signal_plot.setter
  def signal_plot(self,value):
    self._signal_plot = value


class Composer(AbstractSignal):
  def __init__(self, signals):
    super().__init__()
    self._signals = signals
    self._mixed_signals = None

  @property
  def signals(self):
    return self._signals
  @signals.setter
  def signals(self,value):
    self._signals=value

  @property
  def mixed_signals(self):
    composed = 0
    amp =0
    freq = 0
    phase = 0
    for signal in self.signals:
      amp = signal[0]
      freq = signal[1]
      phase = signal[2]
      t = self.linspace
      composed += amp* np.cos(2*np.pi*freq*t + phase)
    self._mixed_signals = composed
    return self._mixed_signals
  @mixed_signals.setter
  def mixed_signals(self,value):
    self._mixed_signals=value

  @property
  def signal(self):
    self._signal = self.mixed_signals
    return self._signal
  @signal.setter
  def signal(self,value):
    
    self._signal=value   
  
  @property
  def signal_plot(self):
    signal = self.signal+self.noise_values
    plot = pg.PlotDataItem(self.linspace, signal)
    self._signal_plot = plot
    return self._signal_plot
  @signal_plot.setter
  def signal_plot(self,value):
    self._signal_plot = value



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 500)
        MainWindow.setStyleSheet("QPushButton{\n"
"border-radius: 30px;\n"
"background-color: green;\n"
"}\n"
"QPushButton:hover{\n"
"border-radius: 30px;\n"
"background-color: red;\n"
"}")
        

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
       
        self.graphicsView = PlotWidget(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(60, 40, 681, 201))
        self.graphicsView.setObjectName("graphicsView")

        signals = [(1,5,0)]
        s = Composer(signals)
        s.SNR = 3
        s.resampling_freq = 125
        self.graphicsView.addItem(s.signal_plot)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
       

        self.retranslateUi(MainWindow)
  
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
       

from pyqtgraph import PlotWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())
