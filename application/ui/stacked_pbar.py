#!/usr/bin/env python

#    Copyright (C) 2021 CARE Trial
#    Email: CARE Trial <care.trial.2019@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
##############################################################################

"""Stacked progress bar module"""

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import sys

StyleSheet = '''
#MainProgressBar {
    text-align: center;
}
#MainProgressBar::chunk {
    background-color: lightblue;
}
'''

class StackedProgressBar(QWidget):
    """Stacked progress bar that has two progress properties."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint
            )

        self.setWindowTitle('Loading')
        width = 550
        height = 100
        self.setMinimumSize(width, height)

        font = QtGui.QFont()
        font.setPointSize(10)

        self.sub_pbar = QProgressBar(self)
        self.sub_pbar.setGeometry(30, 40, 500, 75)

        self.sub_pbarlabel = QLabel(self)
        self.sub_pbarlabel.setGeometry(30, 40, 500, 75)
        self.sub_pbarlabel.setFont(font)
        self.sub_pbarlabel.setText('Processing')

        self.main_pbar = QProgressBar(self, objectName="MainProgressBar")
        self.main_pbar.setGeometry(30, 40, 500, 75)
        self.main_pbar.setStyleSheet(StyleSheet)

        self.main_pbarlabel = QLabel(self)
        self.main_pbarlabel.setGeometry(30, 40, 500, 75)
        self.main_pbarlabel.setFont(font)
        self.main_pbarlabel.setText('Processing')


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.sub_pbarlabel)
        self.layout.addWidget(self.sub_pbar)
        self.layout.addWidget(self.main_pbarlabel)
        self.layout.addWidget(self.main_pbar)

        self.setLayout(self.layout)
        

    def show_pbar(self):  # To restart the progress every time
        self.show()
        
    def start_t(self):
        self.thread.start()

    def on_count_changed(self, value):
        self.sub_pbar.setValue(value)

    def on_text_changed(self, text):
        self.sub_pbarlabel.setText(text)

    def on_main_count_changed(self, value):
        self.main_pbar.setValue(value)

    def on_main_text_changed(self, text):
        self.main_pbarlabel.setText(text)

    def hide_pbar(self):
        self.hide()


# For test
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo Widget")
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    pbar = StackedProgressBar()
    pbar.show_pbar()
    pbar.on_main_count_changed(50)
    pbar.on_main_text_changed('te')
    sys.exit(app.exec_())
    