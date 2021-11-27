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

"""Main window."""

# =============================================================================
# Standard library imports
# =============================================================================
from os.path import isfile, join
import logging
import csv
import os

#==============================================================================
# Third-party imports
#==============================================================================
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHeaderView, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QSettings, Qt, QThread
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt

#==============================================================================
# Local application imports
#==============================================================================
from threads.PatientOverview import PatientOverview
from threads.HourlyView import HourlyView
from ui.ui_main import Ui_MainWindow
from ui.about_dialog import AboutDialog
from ui.settings_dialog import SettingsDialog
from ui.stacked_pbar import StackedProgressBar
from ui.pbar import PopUpProgressBar

#==============================================================================
# Setup Logging
#==============================================================================
# Get the logger specified in the file
logger = logging.getLogger(__name__)

# set mpl figure font size
plt.rcParams.update({'font.size': 12})

class MainWindow(QMainWindow):
    def __init__(self,db):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.about = AboutDialog(self)
        self.settings_dialog = SettingsDialog(self)
        self.pbar = PopUpProgressBar(self)
        self.settings = self.settings_dialog.settings
        self._connectSignals()
        self.db = db
        self._set_TableHeader()

    def _connectSignals(self):
        """Connect signals and slots."""
        # Action bar tab
        self.ui.actionAbout.triggered.connect(self.about.show)
        self.ui.actionSettings.triggered.connect(self.settings_dialog.show)

        # Patient Overview tab
        self.ui.btn_openDirDialog.clicked.connect(self.open_dir_dialog)
        self.ui.btn_startBatchPros.clicked.connect(self.start_PO_analysis)
        self.ui.btn_PO_reset.clicked.connect(self.reset_PO_screen)
        self.ui.btn_PO_export.clicked.connect(self.export_PO_res)

        # Hourly View tab
        self.ui.btn_openFDialog.clicked.connect(self.open_fname_dialog)
        self.ui.btn_reset.clicked.connect(self.reset_HV_screen)
        self.ui.btn_export.clicked.connect(self.export_HV_res)

    def _set_TableHeader(self):
        """Display UI table header"""
        labels = ['Ers\n(cmH\u2082O/L)','Rrs\n(cmH\u2082Os/L)','PEEP\n(cmH\u2082O)','PIP\n(cmH\u2082O)','Vₜ\n(mL)','PIP-PEEP\n(cmH\u2082O)']
        for i in range(len(labels)):
            self.ui.tableWidget.horizontalHeaderItem(i).setText(labels[i])
            self.ui.tableWidget_2.horizontalHeaderItem(i).setText(labels[i])

    def open_fname_dialog(self):
        """Dialog to select filename
           Link to: Hourly View module (def self.start_HV_analysis())
        """
        self.ui.btn_openFDialog.setEnabled(False)
        self.ui.btn_export.setEnabled(False)
        f_input, _ = QFileDialog.getOpenFileName(self,"Locate raw data file to analyze...", "","Text Files (*.txt)", options=QFileDialog.Options())
        if f_input:
            self.fname_full_path = f_input
            self.start_HV_analysis()
        else:
            self.ui.btn_openFDialog.setEnabled(True)  # Re-enable choose btn if user cancel on file selection dialog
 
    def open_dir_dialog(self):
        """Dialog to select directory
           Link to: Patient Overview module (def self.start_PO_analysis())
        """
        dirSelected = str(QFileDialog.getExistingDirectory(self, "Locate directory to analyze...",str(QSettings().value('DEFAULT_DIR'))))
        if dirSelected != "":
            QSettings().setValue('DEFAULT_DIR',dirSelected)
            self.ui.lineEdit_dir.setText(dirSelected)
            logger.info(f'Directory selected: {dirSelected}')
            self.dirSelected = dirSelected
            self.ui.btn_startBatchPros.setEnabled(True)

    def start_HV_analysis(self,**kwargs):
        """Start Hourly View analysis thread"""
        self.ui.statusBar.showMessage("Processing Data")
        self.HVWorker = HourlyView(fname=self.fname_full_path,db=self.db,ui=self.ui)
        self.HVWorker_thread = QThread()
        self.HVWorker.setObjectName('HourlyView')
        self.HVWorker_thread.setObjectName('HourlyViewThread')
        self.HVWorker.moveToThread(self.HVWorker_thread)
        self.HVWorker_thread.started.connect(self.HVWorker.run)
        self.HVWorker.printDebug.connect(self._printDebug)
        self.HVWorker.writeTable.connect(self._writeTable)
        self.HVWorker.open_pbar.connect(self._openPbar)
        self.HVWorker.update_pbar.connect(self._updatePbar)
        self.HVWorker.update_UI.connect(self._updateUI)
        self.HVWorker.finished.connect(self.HVWorker_thread.quit)
        self.HVWorker.done.connect(self.stop_thread)
        self.HVWorker_thread.start()
        logger.info('HourlyView Worker thread started')

    def start_PO_analysis(self):
        """Start Patient Overview analysis thread"""
        # get all files in dirSelected
        files = [f for f in os.listdir(self.dirSelected) if isfile(join(self.dirSelected, f))]
        files_filtered = [f for f in files if f.endswith('.txt')]
        files_filtered = [f for f in files_filtered if f.startswith('patient')]
        files_filtered = [f for f in files_filtered if os.path.getsize(join(self.dirSelected, f)) > 0]
        
        logger.info(f'Files filtered: {files_filtered}')

        # if fileList is not empty
        if len(files_filtered) != 0:
            self.postP = PatientOverview(fname=files_filtered,dirSelected=self.dirSelected,db=self.db,ui=self.ui)
            self.postP_thread = QThread()
            self.postP.moveToThread(self.postP_thread)
            self.postP_thread.started.connect(self.postP.run)
            self.postP_thread.start()
            self.postP.open_pbar.connect(self._openStackedPbar)
            self.postP.hide_pbar.connect(self._hideStackedPbar)
            self.postP.update_subpbar.connect(self._updateStackedPbar)
            self.postP.update_mainpbar.connect(self._updateMainStackedPbar)
            self.postP.final_results.connect(self.process_PO_res)
            self.postP.finished.connect(self.postP_thread.quit)
            self.ui.btn_startBatchPros.setEnabled(False)
        else:
            logger.error('Cannot open folder. Number of files in folder is zero.')
            QMessageBox.critical(None, ("Cannot open folder"),
                                   ("Unable to read files from folder.\n"
                                    "Please ensure folder selected only containes correctly formatted data. "
                                    "Only text files are allowed. "
                                    "Please refer to the CARENet documentation for more information.\n\n"
                                    "Click Cancel to exit."),
                    QMessageBox.Cancel)

    def process_PO_res(self,res):
        """Process final results from Patient Overview Module"""
        # update ui 
        logger.info('_processRes(): Processing completed.')
        self.ui.statusBar.showMessage("Processing completed.")
        self.ui.btn_PO_reset.setEnabled(True)
        self.ui.btn_PO_export.setEnabled(True)
        self.ui.btn_openDirDialog.setEnabled(False)
        self.ui.label_PO_p_no.setText(res['p_no'])
        self.ui.label_PO_date.setText(res['date'])
        if self.settings.value('resolution') == '30mins':
            hours_cnt = int(len(res['hours'])/2)
        else:
            hours_cnt = int(len(res['hours']))
        self.ui.label_t_hours.setText(str(hours_cnt))
        self.ui.label_PO_bCount.setText(str(sum(res['b_count'])))

        # resize table widget (can't be done on thread for some reasons)
        self.ui.tableWidget_2.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
   
    def reset_HV_screen(self):
        """Reset screen in Hourly View Module"""
        self.ui.graphWidget.canvas.ax.cla()
        self.ui.boxGraphWidget.canvas.ax1.cla()
        self.ui.boxGraphWidget.canvas.ax2.cla()
        self.ui.boxGraphWidget.canvas.ax3.cla()
        self.ui.boxGraphWidget.canvas.ax4.cla()
        self.ui.boxGraphWidget.canvas.ax5.cla()
        self.ui.boxGraphWidget.canvas.ax6.cla()
        self.ui.pieGraphWidget.canvas.ax.cla()
        self.ui.AMBoxWidget.canvas.ax.cla()
        self.ui.graphWidget.canvas.draw()
        self.ui.boxGraphWidget.canvas.draw()
        self.ui.pieGraphWidget.canvas.draw()
        self.ui.AMBoxWidget.canvas.draw()
        self.ui.tableWidget.clearContents()
        self.ui.statusBar.showMessage("Screen refreshed")
        self.ui.btn_openFDialog.setEnabled(True)
        self.ui.btn_reset.setEnabled(False)
        self.ui.btn_export.setEnabled(False)
        self.ui.label_AI.setText('')
        self.ui.label_breath_no.setText('')
        self.ui.label_date.setText('')
        self.ui.label_hour.setText('')
        self.ui.label_pat_no.setText('')
        self.ui.norm_breath_label.setText('')
        self.ui.asyn_breath_label.setText('')
        self.ui.total_breath_label.setText('')
        self.ui.ai_breath_label.setText('')

    def reset_PO_screen(self):
        """Reset screen in Patient Overview Module"""
        # Clear plots
        plots = [self.ui.poErsWidget.canvas, self.ui.poRrsWidget.canvas, self.ui.poPIPWidget.canvas,
                self.ui.poPEEPWidget.canvas, self.ui.poVtWidget.canvas, self.ui.poDpWidget.canvas,
                self.ui.poAIWidget.canvas, self.ui.poAMWidget_2.canvas]
        for i in range(len(plots)):
            plots[i].ax.cla()
            plots[i].draw()
     
        self.ui.label_PO_p_no.setText('')
        self.ui.label_PO_date.setText('')
        self.ui.label_t_hours.setText('')
        self.ui.label_PO_bCount.setText('')
        self.ui.label_PO_AI.setText('')
        self.ui.lineEdit_dir.setText('')
        self.ui.tableWidget_2.clearContents()
        self.ui.statusBar.showMessage("Screen refreshed")
        self.ui.btn_PO_export.setEnabled(False)
        self.ui.btn_openDirDialog.setEnabled(True)
        self.ui.btn_PO_reset.setEnabled(False)
       
    def export_PO_res(self):
        """Export results in Patient Overview Module"""
        files = [f for f in os.listdir(self.dirSelected) if isfile(join(self.dirSelected, f))]
        files_sanitised = [f for f in files if f.endswith('.txt')]
        first_file = files_sanitised[0]
        fname = first_file.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        name, _ = QFileDialog.getSaveFileName(self, 'Save File', f'{self.dirSelected}/{date}',"Comma Seperated values (*.csv)")
        
        logger.info(f'User selected export csv filename: {name}')
        if name != "":
            query = QSqlQuery(self.db)
            query.exec(f"""SELECT p_no, date, hour, b_count,
                            Ers_min,   Ers_max,  Ers_q5,  Ers_q25,  Ers_q50,  Ers_q75,  Ers_q95,
                            Rrs_min,   Rrs_max,  Rrs_q5,  Rrs_q25,  Rrs_q50,  Rrs_q75,  Rrs_q95,
                            PEEP_min,  PEEP_max, PEEP_q5, PEEP_q25, PEEP_q50, PEEP_q75, PEEP_q95,
                            PIP_min,   PIP_max,  PIP_q5,  PIP_q25,  PIP_q50,  PIP_q75,  PIP_q95,
                            TV_min,    TV_max,   TV_q5,   TV_q25,   TV_q50,   TV_q75,   TV_q95,
                            DP_min,    DP_max,   DP_q5,   DP_q25,   DP_q50,   DP_q75,   DP_q95,
                            AI_Norm_cnt, AI_Asyn_cnt, AI_Index  FROM results
                            WHERE p_no='{p_no}' AND date='{date}';
                            """)
                
            try:
                with open(name, mode='w', newline='') as csvfile:
                    w = csv.writer(csvfile)
                    # write header
                    w.writerow((
                        'Patient No.','Record Date','Record Hour','Breath Count',
                        'Ers_min', 'Ers_max','Ers_q5','Ers_q25','Ers_q50','Ers_q75','Ers_q95',
                        'Rrs_min', 'Rrs_max','Rrs_q5','Rrs_q25','Rrs_q50','Rrs_q75','Rrs_q95',
                        'PEEP_min', 'PEEP_max','PEEP_q5','PEEP_q25','PEEP_q50','PEEP_q75','PEEP_q95',
                        'PIP_min', 'PIP_max','PIP_q5','PIP_q25','PIP_q50','PIP_q75','PIP_q95',
                        'VT_min', 'VT_max','VT_q5','VT_q25','VT_q50','VT_q75','VT_q95',
                        'PIP-PEEP_min', 'PIP-PEEP_max','PIP-PEEP_q5','PIP-PEEP_q25','PIP-PEEP_q50','PIP-PEEP_q75','PIP-PEEP_q95',
                        'AI_Norm_cnt', 'AI_Asyn_cnt', 'AI_index'
                        ))
                    while query.next():
                        # Write rows
                        listsTmpData = []
                        for column in range(49):
                            listsTmpData.append(str(query.value(column)))
                        w.writerow(listsTmpData)

                # Notify user export done
                self.ui.statusBar.showMessage("Data exported to: "+ name )
                QMessageBox.information(None, ("Data exported"),
                                    ("Data exported to: \n"+ name),
                        QMessageBox.Ok)
            except PermissionError as e:
                # Notify user export failed
                QMessageBox.warning(None, ("Cannot write file"),
                                ('Error writing file: \n' + str(e)),
                QMessageBox.Cancel)

    def export_HV_res(self):
        """Export results in Hourly View Module"""
        fname = self.fname_full_path.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        hour = str(fname.split('_')[3])
        name, _ = QFileDialog.getSaveFileName(self, 'Save File', date,"Comma Seperated values (*.csv)")
        logger.info(f'User selected export csv filename: {name}')
        if name != "":
            query = QSqlQuery(self.db)
            query.exec(f"""SELECT p_no, date, hour, b_count,
                            Ers_min,   Ers_max,  Ers_q5,  Ers_q25,  Ers_q50,  Ers_q75,  Ers_q95,
                            Rrs_min,   Rrs_max,  Rrs_q5,  Rrs_q25,  Rrs_q50,  Rrs_q75,  Rrs_q95,
                            PEEP_min,  PEEP_max, PEEP_q5, PEEP_q25, PEEP_q50, PEEP_q75, PEEP_q95,
                            PIP_min,   PIP_max,  PIP_q5,  PIP_q25,  PIP_q50,  PIP_q75,  PIP_q95,
                            TV_min,    TV_max,   TV_q5,   TV_q25,   TV_q50,   TV_q75,   TV_q95,
                            DP_min,    DP_max,   DP_q5,   DP_q25,   DP_q50,   DP_q75,   DP_q95  FROM results
                            WHERE p_no='{p_no}' AND date='{date}' AND hour='{hour}';
                            """)
            try:
                with open(name, mode='w', newline='') as csvfile:
                    w = csv.writer(csvfile)
                    # write header
                    w.writerow((
                        'Patient No.','Record Date','Record Hour','Breath Count',
                        'Ers_min', 'Ers_max','Ers_q5','Ers_q25','Ers_q50','Ers_q75','Ers_q95',
                        'Rrs_min', 'Rrs_max','Rrs_q5','Rrs_q25','Rrs_q50','Rrs_q75','Rrs_q95',
                        'PEEP_min', 'PEEP_max','PEEP_q5','PEEP_q25','PEEP_q50','PEEP_q75','PEEP_q95',
                        'PIP_min', 'PIP_max','PIP_q5','PIP_q25','PIP_q50','PIP_q75','PIP_q95',
                        'TV_min', 'TV_max','TV_q5','TV_q25','TV_q50','TV_q75','TV_q95',
                        'DP_min', 'DP_max','DP_q5','DP_q25','DP_q50','DP_q75','DP_q95'
                        ))
                    while query.next():
                        # Write file
                        listsTmpData = []
                        for column in range(46):
                            listsTmpData.append(str(query.value(column)))
                        w.writerow(listsTmpData)
                # Notify user export done
                self.ui.statusBar.showMessage("Data exported to: "+ name )
                QMessageBox.information(None, ("Data exported"),
                                    ("Data exported to: \n"+ name),
                        QMessageBox.Ok)
            except PermissionError as e:
                # Notify user export failed
                QMessageBox.warning(None, ("Cannot write file"),
                                ('Error writing file: \n' + str(e)),
                QMessageBox.Cancel)
                
    def _updateUI(self,p_no,date,hour):
        """ Update UI and status after calculation done"""
        # Update UI and status
        self.ui.btn_reset.setEnabled(True)
        self.ui.btn_export.setEnabled(True)
        self.ui.statusBar.showMessage(f"Processing Completed ")
        
        self.ui.label_pat_no.setText(p_no)
        self.ui.label_date.setText(date)
        self.ui.label_hour.setText(hour)
        
        # Resize table headers. Can't be done in thread(reason unknown)
        self.ui.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Hide the progress bar
        self.pbar.hide()
        
    def _openPbar(self):
        self.pbar.show()

    def _updatePbar(self,value,text):
        self.pbar.on_count_changed(value)
        self.pbar.on_text_changed(text)

    def _hidePbar(self):
        self.pbar.hide()

    def _openStackedPbar(self):
        self.spbar = StackedProgressBar(self)
        self.spbar.show()

    def _updateStackedPbar(self,value,text):
        self.spbar.on_count_changed(value)
        self.spbar.on_text_changed(text)

    def _updateMainStackedPbar(self,value,text):
        logger.info(f'Main Pbar: {value},{text}')
        self.spbar.on_main_count_changed(value)
        self.spbar.on_main_text_changed(text)

    def _hideStackedPbar(self):
        self.spbar.hide()

    def stop_thread(self):
        self.HVWorker_thread.requestInterruption()
        if self.HVWorker_thread.isRunning():
            self.HVWorker_thread.quit()
            self.HVWorker_thread.wait()
            logger.info('qthread stopped')
        else:
            logger.info('worker has already exited.')

    def _printDebug(self, debug, b_count):
         # Display debug logs
        txt = ''
        for r in debug['rejected']:
            txt += f'BS {r[0]}: {r[1]}\n' 
        self.ui.plainTextEdit.setPlainText(txt)
        sum_b_counter = f"Summary:\n========================\nNumber of breath analysed: {debug['b_counter'][0]}\nFailed VT check: {debug['b_counter'][1]}\n"\
                        f"Failed Rrs check: {debug['b_counter'][2]}\nFailed Ers check: {debug['b_counter'][3]}\nFailed len(P=Q) check: {debug['b_counter'][4]}\n"\
                        f"Failed len(P) check: {debug['b_counter'][5]}\nTotal number of breath: {b_count}\n========================"
        self.ui.plainTextEdit_2.setPlainText(sum_b_counter)

    def _writeTable(self,res):
        """ Display info on first table """
        params = ['Ers','Rrs','PEEP','PIP','TV','DP']
        font = QFont()
        font.setPointSize(12)
        for i in range(len(params)):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(res[params[i]]['q5']))
            self.ui.tableWidget.setItem(0, i, item)
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(res[params[i]]['q50']) + '\n [ ' +  str(res[params[i]]['q25']) + ' - ' + str(res[params[i]]['q75']) + ' ] ')
            self.ui.tableWidget.setItem(1, i, item)
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(res[params[i]]['q95']))
            self.ui.tableWidget.setItem(2, i, item)


