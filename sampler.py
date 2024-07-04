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
        self.linspace = np.linspace(self.time_range[0], self.time_range[1], self.space_length,
                                    endpoint=False)  # points for x-axis
        self._signal = None  # points for  y-axis
        self.noise_values = None

    @property
    def time_range(self):
        return self._time_range

    @time_range.setter
    def time_range(self, value):
        self._time_range = value

    @property
    def signal_plot(self):
        return self._signal_plot

    @signal_plot.setter
    def signal_plot(self, value):
        self._signal_plot = value

    # plot for the scattered points
    @property
    def resampled_signal_plot(self):
        number_of_samples = self.resampling_freq * (self.time_range[1] - self.time_range[0])
        self.resampling_data = signal.resample(self.signal, num=number_of_samples)
        xnew = np.linspace(self.time_range[0], self.time_range[1], number_of_samples, endpoint=False)

        plt = pg.ScatterPlotItem(xnew, self.resampling_data)
        self.resampled_signal_plot = plt
        return self._resampled_signal_plot

    @resampled_signal_plot.setter
    def resampled_signal_plot(self, value):
        self._resampled_signal_plot = value

    @property
    def resampling_data(self):
        number_of_samples = self.resampling_freq * (self.time_range[1] - self.time_range[0])
        self.resampling_data = signal.resample(self.signal, num=number_of_samples)
        return self._resampling_data

    @resampling_data.setter
    def resampling_data(self, value):
        self._resampling_data = value

    @property
    def SNR(self):
        return self._SNR

    @SNR.setter
    def SNR(self, value):
        self._SNR = (10 ** (value / 10))
        random_numbers = np.random.normal(0, 0.1, self.space_length)
        # remove old noise values if they were added
        if self.noise_values is not None:
            self.signal = self.signal - self.noise_values

        alpha = np.sqrt(np.sum(np.square(np.asarray(self.signal)) / (self._SNR * (np.sum(np.square(random_numbers))))))
        self.noise_values = random_numbers * alpha
        # add new noise values
        self.signal = self.signal + self.noise_values

    @property
    def resampling_freq(self):
        return self._resampling_freq

    @resampling_freq.setter
    def resampling_freq(self, value):
        self._resampling_freq = value

    @property
    def difference_signal_plot(self):
        # recovered_signal = np.asarray(self.sinc_interpolation(self.resampling_data,self.sampling_freq, self.linspace))
        recovered_signal = np.asarray(
            self.sinc_interpolation(self.resampling_data, self.resampling_freq, self.linspace))
        original_signal = np.asarray(self.signal)
        plt = pg.PlotDataItem(self.linspace, original_signal - recovered_signal)
        self.difference_signal_plot = plt
        return self._difference_signal_plot

    @difference_signal_plot.setter
    def difference_signal_plot(self, value):
        self._difference_signal_plot = value

    @property
    def recovered_signal_plot(self):
        # signal = np.asarray(self.sinc_interpolation(self.resampling_data,self.sampling_freq, self.linspace))+self.noise_values
        signal = self.sinc_interpolation(self.resampling_data, self.resampling_freq, self.linspace)
        plt = pg.PlotDataItem(self.linspace, signal)
        self.recovered_signal_plot = plt
        return self._recovered_signal_plot

    @recovered_signal_plot.setter
    def recovered_signal_plot(self, value):
        self._recovered_signal_plot = value

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, value):
        self._signal = value

    def sinc_interpolation(self, sampled_signal, sampling_frequency, linspace):
        # sampling period
        T = 1 / (sampling_frequency)
        # number of samples
        N = len(sampled_signal)
        time_samples = np.arange(0, N * T, T)
        sinc = lambda t: np.sum(np.dot(sampled_signal, np.sinc((t - time_samples) / T)))
        recovered_signal = list(map(sinc, linspace))
        return recovered_signal

class Signal(AbstractSignal):
    def __init__(self, data: np.ndarray):
        super().__init__()
        self._data = data
        self._sampling_freq = 125
        self._samples_number = len(data)

        self._sampling_period = 1 / 125
        self.signal = np.asarray(self.sinc_interpolation(self.data, self.sampling_freq, self.linspace))

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, value):
        self._signal = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def sampling_freq(self):
        return self._sampling_freq

    @sampling_freq.setter
    def sampling_freq(self, value):
        self._sampling_freq = value

    @property
    def samples_number(self):
        return self._samples_number

    @samples_number.setter
    def samples_number(self, value):
        self._samples_number = value

    @property
    def sampling_period(self):
        return self._sampling_period

    @sampling_period.setter
    def sampling_period(self, value):
        self._sampling_period = value

    @property
    def signal_plot(self):
        signal = self.signal
        plot = pg.PlotDataItem(self.linspace, signal)
        self._signal_plot = plot
        return self._signal_plot

    @signal_plot.setter
    def signal_plot(self, value):
        self._signal_plot = value


class Composer(AbstractSignal):
    def __init__(self, signals):
        super().__init__()
        self._signals = signals
        self._mixed_signals = None
        self.signal = self.mixed_signals

    @property
    def signals(self):
        return self._signals

    @signals.setter
    def signals(self, value):
        self._signals = value

    @property
    def mixed_signals(self):
        composed = 0
        amp = 0
        freq = 0
        phase = 0
        for signal in self.signals:
            freq = signal[0]
            amp = signal[1]
            phase = signal[2]
            t = self.linspace
            composed += amp * np.cos(2 * np.pi * freq * t + phase)
        self._mixed_signals = composed

        return self._mixed_signals

    @mixed_signals.setter
    def mixed_signals(self, value):
        self._mixed_signals = value

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, value):
        self._signal = value

    @property
    def signal_plot(self):
        signal = self.signal
        plot = pg.PlotDataItem(self.linspace, signal)
        self._signal_plot = plot
        return self._signal_plot

    @signal_plot.setter
    def signal_plot(self, value):
        self._signal_plot = value
