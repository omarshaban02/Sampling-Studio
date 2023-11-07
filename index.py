from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer

import pyqtgraph as pg
import numpy as np
import pandas as pd
import sys
from pathlib import Path
from res_rc import *  # Import the resource module

from PyQt5.uic import loadUiType
import urllib.request

from sampler import AbstractSignal, Signal, Composer

ui, _ = loadUiType('main.ui')


class MainApp(QMainWindow, ui):

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1450, 900)

        self.signal_data = None
        self.signal = None
        self.mixed_signal = None

        self.signal_is_mixed = False
        self.Fmax_for_mixed_signal = 0

        self.plot_widget1 = pg.PlotWidget(self.graphics_view1)
        self.graphics_view_layout1 = QHBoxLayout(self.graphics_view1)
        self.graphics_view_layout1.addWidget(self.plot_widget1)
        self.graphics_view1.setLayout(self.graphics_view_layout1)
        self.plot_widget1.setObjectName("plot_widget1")
        self.plot_widget1.setBackground((25, 35, 45))
        self.plot_widget1.showGrid(x=True, y=True)
        self.plot_widget1.setLabel("bottom", text="Frequency (Hz)")
        self.plot_widget1.setLabel("left", text="Amplitude (mV)")
        self.plot_widget1.setTitle("Signal and sampled")
        self.plot_widget1.setLimits(xMin=-0.2, xMax=1.2)

        self.plot_widget2 = pg.PlotWidget(self.graphics_view2)
        self.graphics_view_layout2 = QHBoxLayout(self.graphics_view2)
        self.graphics_view_layout2.addWidget(self.plot_widget2)
        self.graphics_view2.setLayout(self.graphics_view_layout2)
        self.plot_widget2.setObjectName("plot_widget2")
        self.plot_widget2.setBackground((25, 35, 45))
        self.plot_widget2.showGrid(x=True, y=True)
        self.plot_widget2.setLabel("bottom", text="Frequency (Hz)")
        self.plot_widget2.setLabel("left", text="Amplitude (mV)")
        self.plot_widget2.setTitle("Recovered signal")

        self.plot_widget3 = pg.PlotWidget(self.graphics_view3)
        self.graphics_view_layout3 = QHBoxLayout(self.graphics_view3)
        self.graphics_view_layout3.addWidget(self.plot_widget3)
        self.graphics_view3.setLayout(self.graphics_view_layout3)
        self.plot_widget3.setObjectName("plot_widget3")
        self.plot_widget3.setBackground((25, 35, 45))
        self.plot_widget3.showGrid(x=True, y=True)
        self.plot_widget3.setLabel("bottom", text="Frequency (Hz)")
        self.plot_widget3.setLabel("left", text="Amplitude (mV)")
        self.plot_widget3.setTitle("Error difference")

        self.plot_mixer_widget = pg.PlotWidget(self.mixer_graph_view)
        self.graphics_view_mixer_layout = QHBoxLayout(self.mixer_graph_view)
        self.graphics_view_mixer_layout.addWidget(self.plot_mixer_widget)
        self.mixer_graph_view.setLayout(self.graphics_view_mixer_layout)
        self.plot_mixer_widget.setObjectName("plot_mixer_widget")
        self.plot_mixer_widget.setBackground((25, 35, 45))
        self.plot_mixer_widget.showGrid(x=True, y=True)
        self.plot_mixer_widget.setLabel("bottom", text="Frequency (Hz)")
        self.plot_mixer_widget.setLabel("left", text="Amplitude (mV)")
        self.plot_mixer_widget.setTitle("Mixed signal")

        self.composed_signals_list = []

        self.create_table_of_signals()
        self.mixer_radioButton.clicked.connect(self.toggle_side_bar)
        self.add_row_btn.clicked.connect(self.add_row)

        self.float_validator = QDoubleValidator()
        self.float_validator.setNotation(QDoubleValidator.StandardNotation)


        self.mix_btn.clicked.connect(self.read_table_data)
        self.add_btn.clicked.connect(self.add_mixed_signal_to_widget1)

        self.SNR_slider.valueChanged.connect(lambda: self.SNR_value_label.setNum(
            self.SNR_slider.value()))

        self.frequency_slider.valueChanged.connect(self.change_samples_according_to_frequency)
        self.frequency_slider.sliderPressed.connect(lambda: self.change_slider_cursor(self.frequency_slider))
        self.frequency_slider.sliderReleased.connect(lambda: self.reset_slider_cursor(self.frequency_slider))

        self.SNR_slider.valueChanged.connect(self.add_noise_to_signal)
        self.SNR_slider.sliderPressed.connect(lambda: self.change_slider_cursor(self.SNR_slider))
        self.SNR_slider.sliderReleased.connect(lambda: self.reset_slider_cursor(self.SNR_slider))

        self.actual_radioButton.toggled.connect(self.toggle_actual_normalized_frequency)

        self.noise_radioButton.toggled.connect(self.toggle_enable_disable_SNR_slider)

        self.open_btn.clicked.connect(self.open_signal_file)

    def create_table_of_signals(self):
        self.table_of_signals.setColumnCount(4)
        self.table_of_signals.setHorizontalHeaderLabels(('Frequency', 'Amplitude', 'Shift', ''))
        self.table_of_signals.setColumnWidth(0, 130)
        self.table_of_signals.setColumnWidth(1, 130)
        self.table_of_signals.setColumnWidth(2, 100)
        self.table_of_signals.setColumnWidth(3, 70)
        self.add_row()

    def add_row(self):
        row = self.table_of_signals.rowCount()
        self.table_of_signals.setRowCount(row + 1)
        self.table_of_signals.setRowHeight(row, 30)

        for col in range(4):  # Add buttons to all columns (0, 1, 2, 3)
            if col == 3:  # For the last column (index 3), add the delete button
                button = QPushButton()
                button.setObjectName(f'delete_btn{row}')
                button.setIcon(QIcon('icons/trash copy.svg'))
                button.setStyleSheet(
                    "QPushButton{background-color: rgba(255,255,255,0); border:1px solid rgba(255,255,255,0);} QPushButton:pressed{margin-top:2px }")
                self.table_of_signals.setCellWidget(row, col, button)
                button.clicked.connect(lambda _, row=row: self.delete_row(row))

    def delete_row(self, row):
        if row >= 0 and row < self.table_of_signals.rowCount():
            for col in range(4):  # Remove widgets/items from all columns (0, 1, 2, 3)
                if col == 3:
                    button = self.table_of_signals.cellWidget(row, col)
                    if button is not None:
                        button.deleteLater()
                else:
                    item = self.table_of_signals.item(row, col)
                    if item is not None:
                        item = None
            self.table_of_signals.removeRow(row)

            # Update the button object names and click connections for the remaining rows
            for i in range(row, self.table_of_signals.rowCount()):
                button = self.table_of_signals.cellWidget(i, 3)
                if button is not None:
                    button.setObjectName(f'delete_btn{i}')
                    button.clicked.disconnect()  # Disconnect previous click connection
                    button.clicked.connect(lambda _, row=i: self.delete_row(row))  # Connect a new click connection

    # In the above code:
    # - We remove the widgets/items from the row that is being deleted, including the delete button.
    # - We then update the button object names and click connections for the remaining rows.
    # - By disconnecting the previous click connection and connecting a new one, we ensure that the lambda function captures the correct row index for each button.

    def toggle_side_bar(self):
        if self.mixer_radioButton.isChecked():
            # for slide activate_slider and disable the other buttons
            new_width = 500
        else:
            new_width = 0
        self.animation = QPropertyAnimation(self.mixer_frame, b"minimumWidth")
        self.animation.setDuration(40)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.mixer_frame.update()

    def open_signal_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV Files (*.csv)', options=options)

        self.signal_is_mixed = False
        self.frequency_slider.setValue(125)
        self.SNR_slider.setValue(10)

        self.signal_data = pd.read_csv(file_name).head().to_numpy()[0]
        self.signal = Signal(self.signal_data)
        self.signal.SNR = self.SNR_slider.value()
        self.signal.resampling_freq = self.frequency_slider.value()

        self.plot_widget1.clear()
        self.plot_widget2.clear()
        self.plot_widget3.clear()

        self.plot_widget1.addItem(self.signal.signal_plot)
        self.plot_widget1.addItem(self.signal.resampled_signal_plot)
        self.plot_widget2.addItem(self.signal.recovered_signal_plot)
        self.plot_widget3.addItem(self.signal.difference_signal_plot)

    def read_table_data(self):
        self.composed_signals_list = []
        num_of_incomplete_rows = 0
        cells_with_str_input_cells = set()
        row_count = self.table_of_signals.rowCount()
        column_count = self.table_of_signals.columnCount()
        for row in range(row_count):
            row_data = []
            for column in range(column_count):
                widget_item = self.table_of_signals.item(row, column)
                if widget_item and widget_item.text and widget_item.text() != "":
                    try:
                        row_data.append(float(widget_item.text()))
                    except ValueError as e:
                        row_data.append(widget_item.text())
                        cells_with_str_input_cells.add(row + 1)
            self.composed_signals_list.append(row_data)
            if len(row_data) != 3:
                num_of_incomplete_rows += 1

        if self.composed_signals_list:
            if num_of_incomplete_rows:
                QMessageBox.warning(None, "Warning",
                                    f"There are {num_of_incomplete_rows} components have incomplete parameters",
                                    QMessageBox.Ok)
            elif cells_with_str_input_cells:
                QMessageBox.critical(None, "Error",
                                     f"Signal in row/s # {cells_with_str_input_cells} have/has a string input",
                                     QMessageBox.Ok)
            else:
                self.plot_mixer_widget.clear()
                self.mixed_signal = Composer(self.composed_signals_list)
                self.mixed_signal.SNR = 10
                self.mixed_signal.resampling_freq = self.frequency_slider.value()
                self.plot_mixer_widget.addItem(self.mixed_signal.signal_plot)
        else:
            QMessageBox.critical(None, "Error", f"No Signals are added", QMessageBox.Ok)

    def add_mixed_signal_to_widget1(self):
        self.signal_is_mixed = True
        self.Fmax_for_mixed_signal = int((np.max(np.asarray(self.composed_signals_list).transpose()[0])))
        self.frequency_slider.setValue(2 * self.Fmax_for_mixed_signal)
        self.SNR_slider.setValue(10)

        self.mixed_signal.SNR = 10
        self.mixed_signal.sampling_freq = int(self.frequency_slider.value())
        self.mixed_signal.resampling_freq = int(self.frequency_slider.value())

        self.plot_widget1.clear()
        self.plot_widget2.clear()
        self.plot_widget3.clear()

        self.plot_widget1.addItem(self.mixed_signal.signal_plot)
        self.plot_widget1.addItem(self.mixed_signal.resampled_signal_plot)
        self.plot_widget2.addItem(self.mixed_signal.recovered_signal_plot)
        self.plot_widget3.addItem(self.mixed_signal.difference_signal_plot)

    def toggle_actual_normalized_frequency(self, checked):
        if checked:  # actual
            self.Fmax_label.setText("Hz")
            self.frequency_slider.setMaximum(250)
            if self.signal and not self.signal_is_mixed:
                self.frequency_slider.setValue(125)
            elif self.signal_is_mixed:
                self.frequency_slider.setValue(self.Fmax_for_mixed_signal * 2)
            if self.signal_is_mixed:
                self.mixed_signal.SNR = self.SNR_slider.value()
            else:
                self.signal.SNR = self.SNR_slider.value()
        else:
            self.Fmax_label.setText("Fmax")
            self.frequency_slider.setMaximum(10)
            if self.signal or self.signal_is_mixed:
                self.frequency_slider.setValue(2)
            if self.signal_is_mixed:
                self.mixed_signal.SNR = self.SNR_slider.value()
            else:
                self.signal.SNR = self.SNR_slider.value()

    def toggle_enable_disable_SNR_slider(self, checked):
        if checked:
            self.SNR_slider.setDisabled(False)
            self.SNR_label.setDisabled(False)
            self.SNR_value_label.setDisabled(False)
            self.dB_label.setDisabled(False)
        else:
            self.SNR_slider.setDisabled(True)
            self.SNR_label.setDisabled(True)
            self.SNR_value_label.setDisabled(True)
            self.dB_label.setDisabled(True)
            # when slider disabled set value 0
            self.SNR_slider.setValue(10)
            self.signal.SNR = 10

    def change_samples_according_to_frequency(self):

        self.plot_widget1.clear()
        self.plot_widget2.clear()
        self.plot_widget3.clear()

        if self.actual_radioButton.isChecked():
            if self.signal_is_mixed:
                self.mixed_signal.SNR = self.SNR_slider.value()
                self.mixed_signal.resampling_freq = self.frequency_slider.value()

                self.plot_widget1.addItem(self.mixed_signal.signal_plot)
                self.plot_widget1.addItem(self.mixed_signal.resampled_signal_plot)
                self.plot_widget2.addItem(self.mixed_signal.recovered_signal_plot)
                self.plot_widget3.addItem(self.mixed_signal.difference_signal_plot)
            else:
                self.signal.SNR = self.SNR_slider.value()
                self.signal.resampling_freq = int(self.frequency_slider.value())

                self.plot_widget1.addItem(self.signal.signal_plot)
                self.plot_widget1.addItem(self.signal.resampled_signal_plot)
                self.plot_widget2.addItem(self.signal.recovered_signal_plot)
                self.plot_widget3.addItem(self.signal.difference_signal_plot)
        else:
            if self.signal_is_mixed:
                self.mixed_signal.SNR = self.SNR_slider.value()
                self.mixed_signal.resampling_freq = int(self.frequency_slider.value() * self.Fmax_for_mixed_signal)

                self.plot_widget1.addItem(self.mixed_signal.signal_plot)
                self.plot_widget1.addItem(self.mixed_signal.resampled_signal_plot)
                self.plot_widget2.addItem(self.mixed_signal.recovered_signal_plot)
                self.plot_widget3.addItem(self.mixed_signal.difference_signal_plot)
            else:
                self.signal.SNR = self.SNR_slider.value()
                self.signal.resampling_freq = int(self.frequency_slider.value() * 62.5)

                self.plot_widget1.addItem(self.signal.signal_plot)
                self.plot_widget1.addItem(self.signal.resampled_signal_plot)
                self.plot_widget2.addItem(self.signal.recovered_signal_plot)
                self.plot_widget3.addItem(self.signal.difference_signal_plot)

    def add_noise_to_signal(self):
        self.plot_widget1.clear()
        self.plot_widget2.clear()
        self.plot_widget3.clear()

        if self.signal_is_mixed:
            self.mixed_signal.SNR = self.SNR_slider.value()
            self.mixed_signal.resampling_freq = int(self.frequency_slider.value())

            self.plot_widget1.addItem(self.mixed_signal.signal_plot)
            self.plot_widget1.addItem(self.mixed_signal.resampled_signal_plot)
            self.plot_widget2.addItem(self.mixed_signal.recovered_signal_plot)
            self.plot_widget3.addItem(self.mixed_signal.difference_signal_plot)

        else:
            self.signal.SNR = self.SNR_slider.value()
            self.signal.resampling_freq = self.frequency_slider.value()

            self.plot_widget1.addItem(self.signal.signal_plot)
            self.plot_widget1.addItem(self.signal.resampled_signal_plot)
            self.plot_widget2.addItem(self.signal.recovered_signal_plot)
            self.plot_widget3.addItem(self.signal.difference_signal_plot)

    def change_slider_cursor(self, slider):
        if self.signal or self.mixed_signal:
            slider.setCursor(Qt.ClosedHandCursor)
        else:
            QMessageBox.critical(None, "Error", "No signal found", QMessageBox.Ok)

    def reset_slider_cursor(self, slider):
        slider.setCursor(Qt.OpenHandCursor)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('qss/darkStyle.qss').read_text())
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
