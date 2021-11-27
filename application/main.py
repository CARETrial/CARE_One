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

"""Main CARE_One executable."""

# =============================================================================
# Standard library imports
# =============================================================================
import os
import sys
import logging.config

#==============================================================================
# Set Environment variables
#==============================================================================
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
os.environ["KERAS_BACKEND"] = "tensorflow"

#==============================================================================
# Third-party imports
#==============================================================================
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen 
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QThread

#==============================================================================
# Setup System path
#==============================================================================
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        base_path = sys._MEIPASS
        
else:
        # we are running in a normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))

#==============================================================================
# Setup Logging
#==============================================================================
log_cfg_path = os.path.join(base_path,'logs/logging.conf')
logging.config.fileConfig(fname=log_cfg_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

#==============================================================================
# Setup System Variables
#==============================================================================
__author__ = 'CARETrial'
__version__ = '1.0.0'
__title__ = 'CARE_One'
# sys.path.insert(1, '/application')



class ImportThread(QThread):
    '''
    Do import of main code within another thread.
    Main application runs when this is done.
    '''

    def __init__(self,splash):
        QThread.__init__(self)
        self.splash = splash

    def run(self):
        """Local application pre-imports"""
        # ==============================================================================
        CAREApp.showSplashMsg(self,f'Version: {__version__}\nImporting modules')
        from ui.mainwindow import MainWindow

        CAREApp.showSplashMsg(self,f'Version: {__version__}\nChecking database')
        from models.query import createTable

        CAREApp.showSplashMsg(self,f'Version: {__version__}\nStarting up')
        


class CAREApp(QApplication):

    def __init__(self):
        QApplication.__init__(self, sys.argv)
        self.setOrganizationName("CARENet")
        self.setOrganizationDomain("caresoft.live")
        self.setApplicationName("CARE_One")
        
        # uncomment to enable highdpi scaling
        # self.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    def openMainWindow(self):
        """Open the main window with any loaded files."""
        from ui.mainwindow import MainWindow

        self.window = MainWindow(self.db)
        self.window.setWindowIcon(QIcon(os.path.join(base_path,'src/logo.png')))
        self.window.show()

    def startup(self):
        """Do startup."""
        logger.info('Program start up')

        # close bootloader splash screen when running in one-file mode,
        # else pass when running directly
        try:
            self.closeBootloaderSplash()
        except:
            pass

        # show the splash screen on normal start
        self.splash = self.makeSplash()
        
        # create thread to import large modules
        self.thread = ImportThread(self.splash)
        self.thread.finished.connect(self.slotStartApplication)
        self.thread.start()
        

    def slotStartApplication(self):
        """Start application after modules imported."""
        from models.query import createTable

        self.db = self.db_handle()

        # standard start main window
        self.openMainWindow()

        # initialize/create db table entry
        createTable(self.db)

        # clear splash when startup done
        self.splash.finish(self.window)

    def closeBootloaderSplash(self):
        """Close bootloader splash screen when running in one-file mode"""
        import pyi_splash

        # Close the splash screen. It does not matter when the call
        # to this function is made, the splash screen remains open until
        # this function is called or the Python program is terminated.
        pyi_splash.close()    

    def makeSplash(self):
        """Create and display the splash screen"""
    
        splash_pix = QPixmap(os.path.join(base_path,'src/splash.png'))

        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setEnabled(False)

        # uncomment to set additional flags to splashscreen
        # splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # Set splash font size
        splash_font = splash.font()
        splash_font.setPixelSize(20)
        splash.setFont(splash_font)

        splash.showMessage("Initializing...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)

        splash.show()

        # Close SplashScreen after 2 seconds (2000 ms)
        # QTimer.singleShot(2000, splash.close)
        return splash

    def showSplashMsg(self,msg):
        """Change text displayed on the splash screen"""
        self.splash.showMessage(msg +"...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)

    def db_handle(self):
        """Create and open database"""
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName="dbb")
        db.setDatabaseName("CARE_One_data.sqlite")
        dbName = db.databaseName()
        conName = db.connectionName()
        if not db.open():
            logger.error("Unable to connect to the database")
            QMessageBox.critical(None, ("Cannot open database"),
                                    ("Unable to establish a database connection.\n"
                                        "This program needs SQLite support. Please read "
                                        "the Qt SQL driver documentation for information "
                                        "how to build it.\n\n"
                                        "Click Cancel to exit."),
                        QMessageBox.Cancel)
            sys.exit(1)
        return db

def run():
    '''Run the main application.'''

    # Start up application
    app = CAREApp()
    app.startup()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()


