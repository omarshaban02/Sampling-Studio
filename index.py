PATH = 'signals/mitbih_train.csv'

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from SignalViewer import SignalViewerLogic, Signal
from PyQt5.QtCore import QTimer

import pyqtgraph as pg

import pandas as pd

import sys
from pathlib import Path
from res_rc import *  # Import the resource module

from PyQt5.uic import loadUiType
import urllib.request

import os
from os import path
import random

ui, _ = loadUiType('main.ui')


# class ShowHideCheckBoxes(QCheckBox):
#     def __int__(self, parent):
#         super().__init__(parent)
#         QCheckBox.__init__(self)


class MainApp(QMainWindow, ui):
    _light_mode = True
    _play_pause_state1 = True
    _play_pause_state2 = True
    _play_pause_state3 = True
    _signal1_is_hide = False
    _signal2_is_hide = False
    _previous_horizontal_scrollBar_value1 = 0
    _previous_vertical_scrollBar_value1 = 0
    _previous_horizontal_scrollBar_value2 = 0
    _previous_vertical_scrollBar_value2 = 0
    _counter_graph1 = 1
    _counter_graph2 = 1
    _pdf_files_counter = 1

    # def delete_item(self, item, list_widget):
    #     row = list_widget.row(item)
    #     list_widget.takeItem(row)
    #
    #     # showHideCheckBox = showHideCheckBoxes(tableOfSignals1)
    #     # tableOfSignals1.setCellWidget(0, 1, showHideCheckBox)
    #     # for row_num in range(tableOfSignals_1.rowCount()):
    #     #     tableOfSignals_1.setCellWidget(0, row_num, showHideCheckBox)

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1500, 900)

        self.plot_widget1 = pg.PlotWidget(self.graphics_view1)
        self.graphics_view_layout1 = QHBoxLayout(self.graphics_view1)
        self.graphics_view_layout1.addWidget(self.plot_widget1)
        self.graphics_view1.setLayout(self.graphics_view_layout1)
        self.plot_widget1.setObjectName("plot_widget1")

        self.plot_widget2 = pg.PlotWidget(self.graphics_view2)
        self.graphics_view_layout2 = QHBoxLayout(self.graphics_view2)
        self.graphics_view_layout2.addWidget(self.plot_widget2)
        self.graphics_view2.setLayout(self.graphics_view_layout2)
        self.plot_widget2.setObjectName("plot_widget2")

        self.sv = SignalViewerLogic(self.plot_widget1)
        self.sv2 = SignalViewerLogic(self.plot_widget2)

        self.snapshots_list = []


        # self.horizontal_scrollBar1.setMinimum(0)
        # self.horizontal_scrollBar1.setMaximum(150)
        # self.sv.xScrollBar = self.horizontal_scrollBar1
        # self.sv2.xScrollBar = self.horizontal_scrollBar2

        self.light_dark_mode_btn.clicked.connect(self.toggle_dark_light_mode)

        self.list_widget1 = self.signals_list1
        self.list_widget2 = self.signals_list2

        # self.list_widget1.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.list_widget2.setContextMenuPolicy(Qt.CustomContextMenu)
        #
        # self.list_widget1.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, self.list_widget1))
        # self.list_widget2.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, self.list_widget2))

        self.toggle_radioButton.clicked.connect(self.activate_slider)

        self.list_widget1.itemChanged.connect(lambda: self.change_signal_name(self.list_widget1))

        self.export_btn1.clicked.connect(lambda: self.choose_graph_to_export(self.plot_widget1))
        self.export_btn2.clicked.connect(lambda: self.choose_graph_to_export(self.plot_widget2))

        self.export_all_btn.clicked.connect(lambda: self.export_all_snapshots)

        # self.export_btn2.clicked.connect(self.export_graph2_as_pdf)

        self.color_btn1.clicked.connect(lambda: self.change_signal_color(self.list_widget1))
        self.color_btn2.clicked.connect(lambda: self.change_signal_color(self.list_widget2))

        # connect the scrollBar with QGraph
        self.sv.xScrollBar = self.horizontal_scrollBar1
        self.sv.yScrollBar = self.vertical_scrollBar1
        self.sv2.xScrollBar = self.horizontal_scrollBar2
        self.sv2.yScrollBar = self.vertical_scrollBar2

        # 1st graphics_view buttons
        self.open_btn1.clicked.connect(lambda list_widget: self.openCSV1(self.list_widget1))
        self.plot_btn1.clicked.connect(self.add_signal_to_graph1)
        self.replay_btn1.clicked.connect(self.replay_active_signal1)
        self.stop_btn1.clicked.connect(self.stop_active_signal1)
        self.reset_view_btn1.clicked.connect(self.reset_view1)
        self.hide_btn1.clicked.connect(self.hide_show_active_signal1)  # head not clear or remove
        self.move_down_btn.clicked.connect(self.move_active_signal1_to_graph2)
        self.zoom_in_btn1.clicked.connect(self.zoom_in_graph1)
        self.zoom_out_btn1.clicked.connect(self.zoom_out_graph1)
        self.clear_btn1.clicked.connect(self.clear_graph1)

        # 2nd graphics_view buttons
        self.open_btn2.clicked.connect(lambda list_widget: self.openCSV2(self.list_widget2))
        self.plot_btn2.clicked.connect(self.add_signal_to_graph2)
        self.replay_btn2.clicked.connect(self.replay_active_signal2)
        self.stop_btn2.clicked.connect(self.stop_active_signal2)
        self.reset_view_btn2.clicked.connect(self.reset_view2)
        self.hide_btn2.clicked.connect(self.hide_show_active_signal2)
        self.move_up_btn.clicked.connect(self.move_active_signal2_to_graph1)
        self.zoom_in_btn2.clicked.connect(self.zoom_in_graph2)
        self.zoom_out_btn2.clicked.connect(self.zoom_out_graph2)
        self.clear_btn2.clicked.connect(self.clear_graph2)

        # synchronous graphics_view
        self.replay_btn3.clicked.connect(self.replay_active_synchronous_signals)
        self.stop_btn3.clicked.connect(self.stop_active_synchronous_signals)
        self.reset_view_btn3.clicked.connect(self.reset_synchronous_views)
        self.hide_btn3.clicked.connect(self.hide_show_active_synchronous_signals)
        self.zoom_in_btn3.clicked.connect(self.zoom_in_synchronous)
        self.zoom_out_btn3.clicked.connect(self.zoom_out_synchronous)
        self.clear_btn3.clicked.connect(self.clear_synchronous)

        # for all play, pause buttons
        self.play_pause_btn1.clicked.connect(self.toggle_play_pause_btn1)
        self.play_pause_btn2.clicked.connect(self.toggle_play_pause_btn2)
        self.play_pause_btn3.clicked.connect(self.toggle_play_pause_btn3)

        self.speedSpinBox_1.valueChanged.connect(
            lambda graph: self.change_speed(self.sv, self.speedSpinBox_1.value()))
        self.speedSpinBox_2.valueChanged.connect(
            lambda graph: self.change_speed(self.sv2, self.speedSpinBox_2.value()))

        self.sv.set_title("Graph Viewer 1")
        self.sv2.set_title("Graph Viewer 2")

        self.apply_limits_checkBox_1.stateChanged.connect(lambda: self.apply_limits(self.sv))
        self.apply_limits_checkBox_2.stateChanged.connect(lambda: self.apply_limits(self.sv2))


        # self.snapshot_btn1.clicked.connect()
        # self.snapshot_btn2.clicked.connect()

    def change_signal_color(self, list_widget):
        dialog = QColorDialog()
        dialog.setOption(QColorDialog.ShowAlphaChannel, on=True)
        new_color = dialog.getColor()
        if new_color.isValid():
            if list_widget == self.list_widget1:
                for sig in self.sv.active_signals:
                    sig.color = new_color
                    pen = pg.mkPen(sig.color, width=3)
                    sig.plot_data_item.setPen(pen)
            elif list_widget == self.list_widget2:
                for sig in self.sv2.active_signals:
                    sig.color = new_color
                    pen = pg.mkPen(sig.color, width=3)
                    sig.plot_data_item.setPen(pen)

    def show_context_menu(self, pos, list_widget):
        item = list_widget.itemAt(pos)
        if item:
            context_menu = QMenu()
            title_action = QAction("Change title", self)
            title_action.triggered.connect(lambda: self.change_signal_name(list_widget))
            context_menu.addAction(title_action)
            context_menu.exec_(list_widget.mapToGlobal(pos))

    def toggle_play_pause_btn1(self):
        if len(self.sv.active_signals) != 0:
            if self._play_pause_state1:
                self.sv.play()
                self._play_pause_state1 = False
                self.toggle_icon_with_mode(self.play_pause_btn1, "pause")
            else:
                self.sv.pause()
                self._play_pause_state1 = True
                self.toggle_icon_with_mode(self.play_pause_btn1, "play")
        else:
            QMessageBox.critical(None, "Error", "There are no signals activated", QMessageBox.Ok)

    def toggle_play_pause_btn2(self):
        if len(self.sv2.active_signals) != 0:
            if self._play_pause_state2:
                self.sv2.play()
                self._play_pause_state2 = False
                self.toggle_icon_with_mode(self.play_pause_btn2, "pause")
            else:
                self.sv2.pause()
                self._play_pause_state2 = True
                self.toggle_icon_with_mode(self.play_pause_btn2, "play")
        else:
            QMessageBox.critical(None, "Error", "There are no signals activated", QMessageBox.Ok)

    def toggle_play_pause_btn3(self):
        if (len(self.sv.active_signals) != 0) or (len(self.sv2.active_signals) != 0):
            if self._play_pause_state3:
                self.sv.play()
                self.sv2.play()
                self._play_pause_state3 = False
                self.toggle_icon_with_mode(self.play_pause_btn3, "pause")
            else:
                self.sv.pause()
                self.sv2.pause()
                self._play_pause_state3 = True
                self.toggle_icon_with_mode(self.play_pause_btn3, "play")
        else:
            QMessageBox.critical(None, "Error", "There are no signals activated", QMessageBox.Ok)

    # def link_horizontal_scrollBar_with_Graph1(self, value):
    #     if value == 0:
    #         self.sv.home_view()
    #     else:
    #         delta = value - self._previous_horizontal_scrollBar_value1
    #         self._previous_horizontal_scrollBar_value1 = value  # Update the previous value
    #         if delta > 0:
    #             # Scroll to the right
    #             self.sv.horizontal_shift(1)
    #         elif delta < 0:
    #             # Scroll to the left
    #             self.sv.horizontal_shift(-1)
    #
    # def link_vertical_scrollBar_with_Graph1(self, value):
    #     if value == 0:
    #         self.sv.home_view()
    #     else:
    #         delta = value - self._previous_vertical_scrollBar_value1
    #         self._previous_vertical_scrollBar_value1 = value  # Update the previous value
    #         if delta > 0:
    #             # Scroll to the right
    #             self.sv.vertical_shift(1)
    #         elif delta < 0:
    #             # Scroll to the left
    #             self.sv.vertical_shift(-1)
    #
    # def link_horizontal_scrollBar_with_Graph2(self, value):
    #     if value == 0:
    #         self.sv2.home_view()
    #     else:
    #         delta = value - self._previous_horizontal_scrollBar_value2
    #         self._previous_horizontal_scrollBar_value2 = value  # Update the previous value
    #         if delta > 0:
    #             # Scroll to the right
    #             self.sv2.horizontal_shift(1)
    #         elif delta < 0:
    #             # Scroll to the left
    #             self.sv2.horizontal_shift(-1)
    #
    # def link_vertical_scrollBar_with_Graph2(self, value):
    #     if value == 0:
    #         self.sv2.home_view()
    #     else:
    #         delta = value - self._previous_vertical_scrollBar_value2
    #         self._previous_vertical_scrollBar_value2 = value  # Update the previous value
    #         if delta > 0:
    #             # Scroll to the right
    #             self.sv2.vertical_shift(1)
    #         elif delta < 0:
    #             # Scroll to the left
    #             self.sv2.vertical_shift(-1)
    #
    # def link_synchronous_scrollBar(self, value):
    #     pass

    def openCSV1(self, plot_widget):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV Files (*.csv)', options=options)
        self.list_widget1.clear()  # every time he press open we clear list and rebuild it
        self._counter_graph1 = 1
        self.sv.load_dataset(file_name, 3)

        for i in range(len(self.sv.signals)):
            list_item = QListWidgetItem(f"{self._counter_graph1} - Signal A")
            list_item.setFlags(Qt.ItemIsSelectable  | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
            list_item.setCheckState(Qt.Checked)
            self.list_widget1.addItem(list_item)
            self._counter_graph1 += 1

    def list_signals_to_plot1(self):
        checked_signals_indices = []
        for i in range(self.list_widget1.count()):
            item = self.list_widget1.item(i)
            if item.checkState() == Qt.Checked:
                checked_signals_indices.append(self.list_widget1.row(item))
        return checked_signals_indices

    def add_signal_to_graph1(self):
        checked_signals_indices = self.list_signals_to_plot1()
        for i in checked_signals_indices:
            if self.sv.signals[i] not in self.sv.plotted_signals:
                self.sv.add_signal(i, f"{i+1} - Signal A ",
                                   (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255)))
        if len(self.sv.plotted_signals) != 0:
            self._play_pause_state1 = False
            self.toggle_icon_with_mode(self.play_pause_btn1, "pause")
        else:
            QMessageBox.critical(None, "Error", "There are no signal checked to plotting", QMessageBox.Ok)

    def openCSV2(self, plot_widget):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV Files (*.csv)', options=options)
        self.list_widget2.clear()  # every time he press open we clear list and rebuild it
        self._counter_graph2 = 1
        self.sv2.load_dataset(file_name, 3)

        for i in range(len(self.sv2.signals)):
            list_item = QListWidgetItem(f"{self._counter_graph2} - Signal B")
            list_item.setFlags(Qt.ItemIsSelectable  | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
            list_item.setCheckState(Qt.Checked)
            self.list_widget2.addItem(list_item)
            self._counter_graph2 += 1

    def list_signals_to_plot2(self):
        checked_signals_indices = []
        for i in range(self.list_widget2.count()):
            item = self.list_widget2.item(i)
            if item.checkState() == Qt.Checked:
                checked_signals_indices.append(self.list_widget2.row(item))
        return checked_signals_indices

    def add_signal_to_graph2(self):
        checked_signals_indices = self.list_signals_to_plot2()
        for i in checked_signals_indices:
            if self.sv2.signals[i] not in self.sv2.plotted_signals:
                self.sv2.add_signal(i, f"{i+1} - Signal B ", (
                int(random.random() * 255), int(random.random() * 255), int(random.random() * 255)))
        if len(self.sv2.plotted_signals) != 0:
            self._play_pause_state2 = False
            self.toggle_icon_with_mode(self.play_pause_btn2, "pause")
        else:
            QMessageBox.critical(None, "Error", "There are no signals checked to plotted", QMessageBox.Ok)

    def replay_active_signal1(self):
        self.sv.replay()
        self.toggle_icon_with_mode(self.play_pause_btn1, "pause")
        self._play_pause_state1 = False
        self.sv.home_view()

    def replay_active_signal2(self):
        self.sv2.replay()
        self.toggle_icon_with_mode(self.play_pause_btn2, "pause")
        self._play_pause_state2 = False
        self.sv2.home_view()

    def replay_active_synchronous_signals(self):
        self.sv.replay()
        self.sv2.replay()
        self.sv.home_view()
        self.sv2.home_view()
        self.toggle_icon_with_mode(self.play_pause_btn3, "pause")
        self._play_pause_state3 = False

    def stop_active_signal1(self):
        self.sv.replay()
        self.toggle_icon_with_mode(self.play_pause_btn1, "play")
        self._play_pause_state1 = True
        self.sv.pause()
        self.sv.home_view()

    def stop_active_signal2(self):
        self.sv2.replay()
        self.toggle_icon_with_mode(self.play_pause_btn2, "play")
        self._play_pause_state2 = True
        self.sv2.pause()
        self.sv2.home_view()

    def stop_active_synchronous_signals(self):
        self.stop_active_signal1()
        self.stop_active_signal2()

    def reset_view1(self):
        self.sv.home_view()
        self.horizontal_scrollBar1.setMinimum(0)

    def reset_view2(self):
        self.sv2.home_view()
        self.horizontal_scrollBar2.setMinimum(0)

    def reset_synchronous_views(self):
        self.reset_view1()
        self.reset_view2()

    def hide_show_active_signal1(self):
        if len(self.sv.active_signals) != 0:
            if self._signal1_is_hide:
                self.sv.show_hidden_signal()
                self.toggle_icon_with_mode(self.play_pause_btn1, "play")
                self._play_pause_state1 = True
                self.toggle_icon_with_mode(self.hide_btn1, "eye")
                self._signal1_is_hide = False
            else:
                self.sv.hide_signal()
                self.sv.pause()
                self.toggle_icon_with_mode(self.hide_btn1, "eye-crossed")
                self._signal1_is_hide = True
                self.toggle_icon_with_mode(self.play_pause_btn1, "play")
                self._play_pause_state1 = True
        else:
            QMessageBox.critical(None, "Error", "There are no signals activated", QMessageBox.Ok)

    def hide_show_active_signal2(self):  # I add button 3 because when function sync run it call this function
        if len(self.sv2.active_signals) != 0:
            if self._signal2_is_hide:
                self.sv2.show_hidden_signal()
                self.toggle_icon_with_mode(self.play_pause_btn2, "play")
                self.toggle_icon_with_mode(self.play_pause_btn3, "play")
                self._play_pause_state2 = True
                self.toggle_icon_with_mode(self.hide_btn2, "eye")
                self.toggle_icon_with_mode(self.hide_btn3, "eye")
                self._signal2_is_hide = False
            else:
                self.sv2.hide_signal()
                self.sv2.pause()
                self.toggle_icon_with_mode(self.hide_btn2, "eye-crossed")
                self.toggle_icon_with_mode(self.hide_btn3, "eye-crossed")
                self._signal2_is_hide = True
                self.toggle_icon_with_mode(self.play_pause_btn2, "play")
                self.toggle_icon_with_mode(self.play_pause_btn3, "play")
                self._play_pause_state2 = True
        else:
            QMessageBox.critical(None, "Error", "There are no signals activated", QMessageBox.Ok)

    def hide_show_active_synchronous_signals(self):
        self.hide_show_active_signal1()
        self.hide_show_active_signal2()

    def move_active_signal1_to_graph2(self):
        if len(self.sv.active_signals) != 0:
            self.sv.moveTo(self.sv2)
            self.sv.pause()
            self.toggle_icon_with_mode(self.play_pause_btn1, "play")
            self._play_pause_state1 = True
            self.sv2.pause()
            self.toggle_icon_with_mode(self.play_pause_btn2, "play")
            self._play_pause_state2 = True
            self.toggle_icon_with_mode(self.hide_btn1, "eye")
            self._signal1_is_hide = False

            self.list_widget1.clear()
            self.list_widget2.clear()
            for i in range(len(self.sv2.signals)):
                list_item = QListWidgetItem(f"{self.sv2.signals[i].title.toPlainText()}")
                list_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Checked)
                self.list_widget2.addItem(list_item)
            for i in range(len(self.sv.signals)):
                list_item = QListWidgetItem(f"{self.sv.signals[i].title.toPlainText()}")
                list_item.setFlags(Qt.ItemIsSelectable  | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Checked)
                self.list_widget1.addItem(list_item)
        else:
            QMessageBox.critical(None, "Error", "There are no signals activated", QMessageBox.Ok)

    def move_active_signal2_to_graph1(self):
        if len(self.sv2.active_signals) != 0:
            self.sv2.moveTo(self.sv)
            self.sv2.pause()
            self.toggle_icon_with_mode(self.play_pause_btn2, "play")
            self._play_pause_state2 = True
            self.sv.pause()
            self.toggle_icon_with_mode(self.play_pause_btn1, "play")
            self._play_pause_state1 = True
            self.toggle_icon_with_mode(self.hide_btn2, "eye")
            self._signal2_is_hide = False

            self.list_widget1.clear()
            self.list_widget2.clear()
            for i in range(len(self.sv.signals)):
                list_item = QListWidgetItem(f"{self.sv.signals[i].title.toPlainText()}")
                list_item.setFlags(Qt.ItemIsSelectable  | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Checked)
                self.list_widget1.addItem(list_item)
            for i in range(len(self.sv2.signals)):
                list_item = QListWidgetItem(f"{self.sv2.signals[i].title.toPlainText()}")
                list_item.setFlags(Qt.ItemIsSelectable  | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Checked)
                self.list_widget2.addItem(list_item)
        else:
            QMessageBox.critical(None, "Error", "There are no signals activated", QMessageBox.Ok)

    def change_speed(self, graph, new_speed):
        if new_speed:
            graph.rate = new_speed

    def change_color(self, signals_list, new_color):
        for signal in signals_list:
            signal.color = self.color_dict[new_color]
            pen = pg.mkPen(signal.color, width=3)
            signal.plot_data_item.setPen(pen)

    def zoom_in_graph1(self):
        view_box1 = self.plot_widget1.getViewBox()
        view_box1.scaleBy(s=(0.9, 0.9))
        print(dir(view_box1))

    def zoom_out_graph1(self):
        view_box1 = self.plot_widget1.getViewBox()
        view_box1.scaleBy((1.1, 1.1))

    def zoom_in_graph2(self):
        view_box2 = self.plot_widget2.getViewBox()
        view_box2.scaleBy((0.9, 0.9))

    def zoom_out_graph2(self):
        view_box2 = self.plot_widget2.getViewBox()
        view_box2.scaleBy((1.1, 1.1))

    def zoom_in_synchronous(self):
        self.zoom_in_graph1()
        self.zoom_in_graph2()

    def zoom_out_synchronous(self):
        self.zoom_out_graph1()
        self.zoom_out_graph2()

    def clear_graph1(self):
        if len(self.sv.plotted_signals) != 0:
            self.list_widget1.clear()
            self.sv.clear()
            self.sv.home_view()
            self.toggle_icon_with_mode(self.play_pause_btn1, "play")
        else:
            QMessageBox.critical(None, "Error", "There are no signals plotted", QMessageBox.Ok)

    def clear_graph2(self):
        if len(self.sv2.plotted_signals) != 0:
            self.list_widget2.clear()
            self.sv2.clear()
            self.sv2.home_view()
            self.toggle_icon_with_mode(self.play_pause_btn2, "play")
            self.toggle_icon_with_mode(self.play_pause_btn3, "play")
        else:
            QMessageBox.critical(None, "Error", "There are no signals plotted", QMessageBox.Ok)

    def clear_synchronous(self):  # I donot call the 2 above function because the message box will call twice
        if len(self.sv.plotted_signals) != 0 or len(self.sv2.plotted_signals) != 0:
            self.list_widget1.clear()
            self.sv.clear()
            self.sv.home_view()
            self.toggle_icon_with_mode(self.play_pause_btn1, "play")

            self.list_widget2.clear()
            self.sv2.clear()
            self.sv2.home_view()
            self.toggle_icon_with_mode(self.play_pause_btn2, "play")
            self.toggle_icon_with_mode(self.play_pause_btn3, "play")
        else:
            QMessageBox.critical(None, "Error", "There are no signals plotted at any graph", QMessageBox.Ok)

    def export_graph1_as_pdf(self):
        if len(self.sv.plotted_signals) != 0:
            self.sv.exportPDF(f"Signal Viewer Statistics {self._pdf_files_counter}")
            self._pdf_files_counter += 1
        else:
            QMessageBox.critical(None, "Error", "There are no signals in the graph", QMessageBox.Ok)

    def export_graph2_as_pdf(self):
        if len(self.sv2.plotted_signals) != 0:
            self.sv2.exportPDF("Signal Viewer Statistics")
            self.sv.exportPDF(f"Signal Viewer Statistics {self.df_files_counter}")
            self._pdf_files_counter += 1
        else:
            QMessageBox.critical(None, "Error", "There are no signals in the graph", QMessageBox.Ok)

    def change_signal_name(self, list_widget):
        item = list_widget.currentItem()
        if list_widget == self.list_widget1:
            self.sv.signals[list_widget.row(item) - 1].title = item.text()
            self.sv.set_signal_title(self.sv.signals[list_widget.row(item) - 1], item.text())
        elif list_widget == self.list_widget2:
            self.sv2.signals[list_widget.row(item) - 1].title = item.text()
            self.sv2.set_signal_title(self.sv2.signals[list_widget.row(item) - 1], item.text())

    def toggle_icon_with_mode(self, button, icon_name=""):
        if self._light_mode:
            button.setIcon(QIcon(f'icons/{icon_name}.svg'))
        else:
            button.setIcon(QIcon(f'icons/{icon_name} copy.svg'))

    def toggle_eye_icon_with_mode(self, button, signal_is_hide):
        if signal_is_hide:
            self.toggle_icon_with_mode(button, "eye-crossed")
            signal_is_hide = False
        else:
            self.toggle_icon_with_mode(button, "eye")

    def activate_slider(self):
        self.sv.pause()
        self.sv2.pause()
        self.sv.home_view()
        self.sv2.home_view()
        if self.toggle_radioButton.isChecked():
            # link to scrollBar
            self.sv.linkTo(self.sv2)

            # for change icons
            self._play_pause_state1 = False
            self._play_pause_state2 = False
            self.toggle_icon_with_mode(self.play_pause_btn1, "play")
            self.toggle_icon_with_mode(self.play_pause_btn2, "play")

            # for slide activate_slider and disable the other buttons
            new_width = 60
            self.play_pause_btn1.setEnabled(False)
            self.replay_btn1.setEnabled(False)
            self.stop_btn1.setEnabled(False)
            self.reset_view_btn1.setEnabled(False)
            self.hide_btn1.setEnabled(False)
            self.move_up_btn.setEnabled(False)
            self.zoom_in_btn1.setEnabled(False)
            self.zoom_out_btn1.setEnabled(False)
            self.clear_btn1.setEnabled(False)
            self.snapshot_btn1.setEnabled(False)


            self.play_pause_btn2.setEnabled(False)
            self.replay_btn2.setEnabled(False)
            self.stop_btn2.setEnabled(False)
            self.reset_view_btn2.setEnabled(False)
            self.hide_btn2.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            self.zoom_in_btn2.setEnabled(False)
            self.zoom_out_btn2.setEnabled(False)
            self.clear_btn2.setEnabled(False)
            self.snapshot_btn2.setEnabled(False)


        else:

            self.sv.linkTo(None)

            self._play_pause_state1 = True
            self._play_pause_state2 = True

            new_width = 0

            self.play_pause_btn1.setEnabled(True)
            self.replay_btn1.setEnabled(True)
            self.stop_btn1.setEnabled(True)
            self.reset_view_btn1.setEnabled(True)
            self.hide_btn1.setEnabled(True)
            self.move_up_btn.setEnabled(True)
            self.zoom_in_btn1.setEnabled(True)
            self.zoom_out_btn1.setEnabled(True)
            self.clear_btn1.setEnabled(True)
            self.snapshot_btn1.setEnabled(True)


            self.play_pause_btn2.setEnabled(True)
            self.replay_btn2.setEnabled(True)
            self.stop_btn2.setEnabled(True)
            self.reset_view_btn2.setEnabled(True)
            self.hide_btn2.setEnabled(True)
            self.move_down_btn.setEnabled(True)
            self.zoom_in_btn2.setEnabled(True)
            self.zoom_out_btn2.setEnabled(True)
            self.clear_btn2.setEnabled(True)
            self.snapshot_btn2.setEnabled(True)


            self._play_pause_state3 = True
            self.toggle_icon_with_mode(self.play_pause_btn3, "play")

        self.animation = QPropertyAnimation(self.left_side_bar, b"minimumWidth")
        self.animation.setDuration(40)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.left_side_bar.update()

    def toggle_dark_light_mode(self):
        if self._light_mode:
            self.setStyleSheet(Path('qss/darkStyle.qss').read_text())
            self.sv.background_color = (25, 35, 45)
            self.sv2.background_color = (25, 35, 45)
            self.sv.pause()
            self.sv2.pause()
            self.light_dark_mode_btn.setIcon(QIcon('icons/moon copy.svg'))

            self.play_pause_btn1.setIcon(QIcon('icons/play copy.svg'))
            self.replay_btn1.setIcon(QIcon('icons/rewind copy.svg'))
            self.stop_btn1.setIcon(QIcon('icons/stop-button copy.svg'))
            self.reset_view_btn1.setIcon(QIcon('icons/arrow-up-right-and-arrow-down-left-from-center copy.svg'))
            if self._signal1_is_hide:
                self.hide_btn1.setIcon(QIcon('icons/eye-crossed copy.svg'))
            else:
                self.hide_btn1.setIcon(QIcon('icons/eye copy.svg'))
            self.move_up_btn.setIcon(QIcon('icons/up copy.svg'))
            self.zoom_in_btn1.setIcon(QIcon('icons/zoom_in.svg'))
            self.zoom_out_btn1.setIcon(QIcon('icons/zoom_out.svg'))
            self.clear_btn1.setIcon(QIcon('icons/trash copy.svg'))
            self.snapshot_btn1.setIcon(QIcon('icons/camera-viewfinder copy.svg'))

            self.play_pause_btn2.setIcon(QIcon('icons/play copy.svg'))
            self.replay_btn2.setIcon(QIcon('icons/rewind copy.svg'))
            self.stop_btn2.setIcon(QIcon('icons/stop-button copy.svg'))
            self.reset_view_btn2.setIcon(QIcon('icons/arrow-up-right-and-arrow-down-left-from-center copy.svg'))
            if self._signal2_is_hide:
                self.hide_btn2.setIcon(QIcon('icons/eye-crossed copy.svg'))
            else:
                self.hide_btn2.setIcon(QIcon('icons/eye copy.svg'))
            self.move_down_btn.setIcon(QIcon('icons/down copy.svg'))
            self.zoom_in_btn2.setIcon(QIcon('icons/zoom_in.svg'))
            self.zoom_out_btn2.setIcon(QIcon('icons/zoom_out.svg'))
            self.clear_btn2.setIcon(QIcon('icons/trash copy.svg'))
            self.snapshot_btn2.setIcon(QIcon('icons/camera-viewfinder copy.svg'))


            self.play_pause_btn3.setIcon(QIcon('icons/play copy.svg'))
            self.replay_btn3.setIcon(QIcon('icons/rewind copy.svg'))
            self.stop_btn3.setIcon(QIcon('icons/stop-button copy.svg'))
            self.reset_view_btn3.setIcon(QIcon('icons/arrow-up-right-and-arrow-down-left-from-center copy.svg'))
            if self._signal1_is_hide or self._signal2_is_hide:
                self.hide_btn3.setIcon(QIcon('icons/eye-crossed copy.svg'))
            else:
                self.hide_btn3.setIcon(QIcon('icons/eye copy.svg'))
            self.zoom_in_btn3.setIcon(QIcon('icons/zoom_in.svg'))
            self.zoom_out_btn3.setIcon(QIcon('icons/zoom_out.svg'))
            self.clear_btn3.setIcon(QIcon('icons/trash copy.svg'))
            self.snapshot_btn3.setIcon(QIcon('icons/camera-viewfinder copy.svg'))


            self._light_mode = False
        else:
            self.setStyleSheet(Path('qss/lightStyle.qss').read_text())
            self.sv.background_color = (255, 255, 255)
            self.sv2.background_color = (255, 255, 255)
            self.sv.pause()
            self.sv2.pause()
            self.light_dark_mode_btn.setIcon(QIcon('icons/brightness.svg'))

            self.play_pause_btn1.setIcon(QIcon('icons/play.svg'))
            self.replay_btn1.setIcon(QIcon('icons/rewind.svg'))
            self.stop_btn1.setIcon(QIcon('icons/stop-button.png'))
            self.reset_view_btn1.setIcon(QIcon('icons/arrow-up-right-and-arrow-down-left-from-center.svg'))
            if self._signal1_is_hide:
                self.hide_btn1.setIcon(QIcon("icons/eye-crossed.svg"))
            else:
                self.hide_btn1.setIcon(QIcon("icons/eye.svg"))
            self.move_up_btn.setIcon(QIcon('icons/up.svg'))
            self.zoom_in_btn1.setIcon(QIcon('icons/zoom-in (1).png'))
            self.zoom_out_btn1.setIcon(QIcon('icons/magnifying-glass.png'))
            self.clear_btn1.setIcon(QIcon('icons/trash.svg'))
            self.snapshot_btn1.setIcon(QIcon('icons/camera-viewfinder.svg'))


            self.play_pause_btn2.setIcon(QIcon('icons/play.svg'))
            self.replay_btn2.setIcon(QIcon('icons/rewind.svg'))
            self.stop_btn2.setIcon(QIcon('icons/stop-button.png'))
            self.reset_view_btn2.setIcon(QIcon('icons/arrow-up-right-and-arrow-down-left-from-center.svg'))
            if self._signal2_is_hide:
                self.hide_btn2.setIcon(QIcon('icons/eye-crossed.svg'))
            else:
                self.hide_btn2.setIcon(QIcon('icons/eye.svg'))
            self.move_down_btn.setIcon(QIcon('icons/down.svg'))
            self.zoom_in_btn2.setIcon(QIcon('icons/zoom-in (1).png'))
            self.zoom_out_btn2.setIcon(QIcon('icons/magnifying-glass.png'))
            self.clear_btn2.setIcon(QIcon('icons/trash.svg'))
            self.snapshot_btn2.setIcon(QIcon('icons/camera-viewfinder.svg'))


            self.play_pause_btn3.setIcon(QIcon('icons/play.svg'))
            self.replay_btn3.setIcon(QIcon('icons/rewind.svg'))
            self.stop_btn3.setIcon(QIcon('icons/stop-button.png'))
            self.reset_view_btn3.setIcon(QIcon('icons/arrow-up-right-and-arrow-down-left-from-center.svg'))
            if self._signal2_is_hide or self._signal1_is_hide:
                self.hide_btn3.setIcon(QIcon('icons/eye-crossed.svg'))
            else:
                self.hide_btn3.setIcon(QIcon('icons/eye.svg'))
            self.zoom_in_btn3.setIcon(QIcon('icons/zoom-in (1).png'))
            self.zoom_out_btn3.setIcon(QIcon('icons/magnifying-glass.png'))
            self.clear_btn3.setIcon(QIcon('icons/trash.svg'))
            self.snapshot_btn3.setIcon(QIcon('icons/camera-viewfinder.svg'))

            self._light_mode = True

    def apply_limits(self, signal_view):
        signal_view.apply_limits = not signal_view.apply_limits

    def choose_graph_to_export(self, plot_widget):
        pass

    def take_snapshot(self):
        pass

    def export_all_snapshots(self):
        pass



def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('qss/lightStyle.qss').read_text())
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
