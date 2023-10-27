PATH = 'signals/mitbih_train.csv'

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer

import pyqtgraph as pg


import sys
from pathlib import Path
from res_rc import *  # Import the resource module

from PyQt5.uic import loadUiType
import urllib.request


ui, _ = loadUiType('main.ui')



class MainApp(QMainWindow, ui):

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1200, 900)

        self.create_table_of_signals()
        self.mixer_radioButton.clicked.connect(self.activate_slider)
        self.add_row_btn.clicked.connect(self.add_row)

    def create_table_of_signals(self):
        self.table_of_signals.setColumnCount(4)
        self.table_of_signals.setHorizontalHeaderLabels(('Frequency', 'Amplitude', 'shift', ''))
        self.table_of_signals.setColumnWidth(0, 110)
        self.table_of_signals.setColumnWidth(1, 110)
        self.table_of_signals.setColumnWidth(2, 110)
        self.table_of_signals.setColumnWidth(3, 52)

    def add_row(self):
        row = self.table_of_signals.rowCount()
        self.table_of_signals.setRowCount(row + 1)
        self.table_of_signals.setRowHeight(row, 30)



        for col in range(4):  # Add buttons to all columns (0, 1, 2, 3)
            if col == 3:  # For the last column (index 3), add the delete button
                button = QPushButton()
                button.setObjectName(f'delete_btn{row}')
                button.setIcon(QIcon('icons/trash.svg'))
                button.setStyleSheet("QPushButton{background-color: rgba(255,255,255,0); border:1px solid rgba(255,255,255,0);} QPushButton:pressed{margin-top:2px }")
                self.table_of_signals.setCellWidget(row, col, button)
                button.clicked.connect(lambda _, row=row: self.delete_row(row))
            else:
                double_validator = QDoubleValidator()
                double_validator.setNotation(QDoubleValidator.StandardNotation)
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)  # Center-align the text
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                item.setValidator(double_validator)

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

    def activate_slider(self):
        if self.mixer_radioButton.isChecked():
            # for slide activate_slider and disable the other buttons
            new_width = 415
        else:
            new_width = 0
        self.animation = QPropertyAnimation(self.mixer_frame, b"minimumWidth")
        self.animation.setDuration(40)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.mixer_frame.update()




def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('qss/darkStyle.qss').read_text())
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
