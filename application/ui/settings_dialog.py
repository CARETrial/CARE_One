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

"""Settings Dialog module"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QApplication, QWidget
import sys
import logging

# For test
if __name__ == '__main__':
    from ui_settings import Ui_SettingsDialog
else:
    from ui.ui_settings import Ui_SettingsDialog

# Get the logger specified in the file
logger = logging.getLogger(__name__)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setWindowTitle("Widget")
        layout = QVBoxLayout(self)
        btn1 = QPushButton("Open Settings")
        layout.addWidget(btn1)
        btn1.clicked.connect(self.show_settings_dialog)

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.show()
        # if dialog.settings.value('resolution') == '30mins':
        #     dialog.ui.radioButton.setChecked(True)

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent=parent)
        self.ui = Ui_SettingsDialog()
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint
            )
        self.ui.setupUi(self)
        # self.settings = QSettings("My Organization", "My Application")
        self.settings = QSettings()
        # self.settings.value('saveDB',True, type=bool)
        self.initUI()

    def initUI(self):

        if self.settings.contains("saveDB"):
            # there is the key in QSettings
            # if dialog.settings.value('key') == 'value':
            if self.settings.value('saveDB', True, type=bool) == True:
                # Initialize UI with saved settings from QSettings 
                self.ui.saveDBTrue.setChecked(True)
            else:
                self.ui.saveDBFalse.setChecked(True)
        else:
            # there is no key in QSettings
            self.settings.setValue('saveDB',True)
            self.ui.saveDBTrue.setChecked(True)

        
    def saveSettings(self,key,value):
        self.settings.setValue(key,value)
    
    def accept(self):

        if self.ui.saveDBTrue.isChecked():
            self.settings.setValue('saveDB',True)
            logger.info(f'Save DB set: True')
        else:
            self.settings.setValue('saveDB',False)
            logger.info(f'Save DB set: False')

        QMessageBox.information(None, ("Information"),
                                    ("Settings saved successfully.\n"
                                     "Please restart application for changes to take effect."
                                        ),
                        QMessageBox.Ok)
        self.close()



# Tests
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
        
