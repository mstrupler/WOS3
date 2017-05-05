# -*- coding: utf-8 -*-
"""
Created on Thu May  4 10:01:05 2017

@author: mathiasstrupler
"""

import sys
from PyQt4 import QtCore, QtGui, uic
import wok3
from pathlib import Path
import datetime 

qtCreatorFile = "bibliograph.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

VERSION = '0.03a'

def unpackstr(a):
    return a[1:-1]
    
def unpackPosixPath(path):
    return Path(path[11:-2])
    
def unpackBool(string):
    if string=='True':
        return True
    else:
        return False
    
UNPACK = {'int':int,'str':unpackstr,'bool':unpackBool,'pathlib.PosixPath':unpackPosixPath}

    

class MyApp(QtGui.QMainWindow, Ui_MainWindow):

   
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        self.pbNewProject.clicked.connect(self.newProject)
        self.pbLoadProject.clicked.connect(self.loadProject)
        self.pbSaveProject.clicked.connect(self.saveProject)
        self.leTimeSpanFrom.editingFinished.connect(self.setTimeSpanStart)
        self.leTimeSpanTo.editingFinished.connect(self.setTimeSpanEnd)
        self.leQuery.editingFinished.connect(self.setSearchQuery)
        self.progressBar.valueChanged.connect(self.changeProgressLabel)

        self.projectStatus = {}
        
        
        #self.searchThread = QtCore.QThread()
        #self.searchThread.start()
        
        self.searchWOS = SearchWOS()
        #self.searchWOS.moveToThread(self.searchThread)
        
        self.pbPause.clicked.connect(self.searchWOS.pause)
        self.pbSearch.clicked.connect(self.searchWOS.run)
        self.searchWOS.searchFinished.connect(self.searchFinished)
        self.searchWOS.retrievedUpdated.connect(self.updateSearchProgress)
        self.searchWOS.totalUpdated.connect(self.updateSearchTotal)
     
    @QtCore.pyqtSlot(int) 
    def updateSearchProgress(self,retrieved):
        self.projectStatus['retrievedRecords'] = retrieved
        self.projectFileWrite() 
        self.progressBar.setValue(retrieved)
        
    @QtCore.pyqtSlot(int) 
    def updateSearchTotal(self,total):  
        self.projectStatus['retrievedRecords'] = total
        self.projectFileWrite() 
        self.progressBar.setValue(total)
        
    @QtCore.pyqtSlot()
    def searchFinished(self):
        self.pbResume.setEnabled(False)
        self.pbCreateDB.setEnabled(True)

    def changeProgressLabel(self):
        self.lProgress.setText(str(self.progressBar.value())+'/'+str(self.progressBar.maximum()))

        
    def initializeProjectStatus(self):
        self.projectStatus = {}
        self.projectStatus['version'] = VERSION
        self.projectStatus['projectFile'] = None
        self.projectStatus['searchQuery'] = None
        self.projectStatus['timeSpanStart'] = None
        self.projectStatus['timeSpanEnd'] = None
        
        self.projectStatus['totalRecords'] = 0
        self.projectStatus['retrievedRecords'] = 0
        self.projectStatus['UID_DBPos'] = 0
        self.projectStatus['UID_DBSize'] = 0
        
        self.projectStatus['UID_DB_Started'] = False
        self.projectStatus['UID_DB_Finished'] = False
        self.projectStatus['searchStarted'] = False
        self.projectStatus['searchFinished'] = False
        self.projectStatus['citeSearchStarted'] = False
        self.projectStatus['citeSearchFinished'] = False
        self.projectStatus['graphStarted'] = False
        self.projectStatus['graphFinished'] = False
        
    def setSearchQuery(self):
        print(self.leQuery.text())
        self.projectStatus['searchQuery'] = self.leQuery.text()
        self.searchWOS.setQuery(self.projectStatus['searchQuery'])
        self.pbSearch.setEnabled(True)
        self.projectFileWrite() 
    
    def setTimeSpanStart(self):
        print(self.leTimeSpanFrom.text())
        self.projectStatus['timeSpanStart'] = int(self.leTimeSpanFrom.text())
        self.searchWOS.setTimeSpanStart(self.projectStatus['timeSpanStart'])
        self.projectFileWrite() 
        
    def setTimeSpanEnd(self):
        print(self.leTimeSpanTo.text())
        self.projectStatus['timeSpanEnd'] = int(self.leTimeSpanTo.text())
        self.searchWOS.setTimeSpanEnd(self.projectStatus['timeSpanEnd'])
        self.projectFileWrite() 
        
    def saveProject(self):
        self.projectFileWrite()  
        
    def newProject(self):
       fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save project as','./')
       if fileName:
          self.initializeProjectStatus()
          my_file = Path(fileName)
          self.projectStatus['projectFile']=my_file.with_suffix('.bgp')
          self.projectFileWrite()
          
          projectFile = self.projectStatus['projectFile']
          self.searchWOS.setSaveSettings(projectFile)
          self.leFolder.setText(str(projectFile.parent))
          self.leProjectName.setText(projectFile.stem)
          self.leFolder.setEnabled(True)
          self.leProjectName.setEnabled(True)
          self.leTimeSpanTo.setEnabled(True)
          self.leQuery.setEnabled(True)
          self.leTimeSpanFrom.setEnabled(True)
          
    def loadProject(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open project file','./ProjectOCT/',filter='Bibiograph project files (*.bgp)')
        if fileName:
            my_file = Path(fileName)
            self.projectFileRead(my_file)
            projectFile = self.projectStatus['projectFile']
            self.leFolder.setText(str(projectFile.parent))
            self.leProjectName.setText(projectFile.stem)
            self.searchWOS.setSaveSettings(projectFile)
            
            if self.projectStatus['searchQuery'] is not None:
                self.leQuery.setText(self.projectStatus['searchQuery'])
            if self.projectStatus['timeSpanStart'] is not None:
                self.leTimeSpanFrom.setText(str(self.projectStatus['timeSpanStart']))
            if self.projectStatus['timeSpanEnd'] is not None:
                self.leTimeSpanTo.setText(str(self.projectStatus['timeSpanEnd']))
            
                        
            
            self.leFolder.setEnabled(True)
            self.leProjectName.setEnabled(True)
            self.leTimeSpanTo.setEnabled(True)
            self.leQuery.setEnabled(True)
            self.leTimeSpanFrom.setEnabled(True) 
            
            if self.projectStatus['searchStarted']:
                self.leTimeSpanTo.setEnabled(False)
                self.leQuery.setEnabled(False)
                self.leTimeSpanFrom.setEnabled(False) 
                self.pbSearch.setEnabled(False)
                self.pbResume.setEnabled(True)
                self.progressBar.setMaximum(self.projectStatus['totalRecords'])
                self.progressBar.setValue(self.projectStatus['retrievedRecords'])
            if self.projectStatus['searchFinished']:
                self.searchFinished()
            if self.projectStatus['UID_DB_Started']:
                self.pbResume.setEnabled(True)
                self.pbCreateDB.setEnabled(False)
                self.progressBar.setMaximum(self.projectStatus['totalRecords'])
                self.progressBar.setValue(self.projectStatus['UID_DBPos'])
            if self.projectStatus['UID_DB_Finished']:
                self.pbResume.setEnabled(False)
                self.pbSearchCitation.setEnabled(True)
            if self.projectStatus['citeSearchStarted']:
                self.pbResume.setEnabled(True)
                self.pbSearchCitation.setEnabled(False)
                self.progressBar.setMaximum(self.projectStatus['totalRecords'])
                self.progressBar.setValue(self.projectStatus['UID_DBPos'])
            if self.projectStatus['citeSearchFinished']:
                self.pbResume.setEnabled(False)
                self.pbGraph.setEnabled(True)  
            if self.projectStatus['graphStarted']:
                self.pbResume.setEnabled(True)
                self.pbGraph.setEnabled(False) 
                self.progressBar.setMaximum(self.projectStatus['UID_DBSize'])
                self.progressBar.setValue(self.projectStatus['UID_DBPos'])
            if self.projectStatus['graphFinished']:
                self.pbResume.setEnabled(False) 
            
       
    def projectFileWrite(self):
        with self.projectStatus['projectFile'].open('w') as f:
            for key,value in self.projectStatus.items():
                tmp = (type(value),value)
                f.write(key +'\t' + str(tmp) +'\n')

                    
    def projectFileRead(self,filename):
        with filename.open('r') as f:
            lines = f.readlines()
            status = {}
            for line in lines:
                cells = line[:-1].split('\t')
                key = cells[0]
                tmp = cells[1][1:-1].split(',')
                value_type = tmp[0][8:-2]
                value = tmp[1][1:]
                if value=='None':
                    status[key] = None
                else:
                    status[key] = UNPACK[value_type](value)     
            if status['version']==VERSION:
                self.projectStatus = status
            else:
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Warning)
                msg.setText('This file was created using version ' \
                    + str(status['version']) \
                    + 'which is incompatible with this software version (' \
                    + str(VERSION) \
                    + ')')
                msg.exec()
                
            
class SearchWOS(QtCore.QObject):
    searchFinished = QtCore.pyqtSignal()
    retrievedUpdated = QtCore.pyqtSignal(int)
    totalUpdated = QtCore.pyqtSignal(int)
        
    def __init__(self,**kwargs):
        QtCore.QObject.__init__(self)
        self.exiting = False
        self.firstsearch = True
        self.finished = False
        self.retrieved = 0
        self.total = 0
        
        if kwargs is not None: 
            if 'proxy' in kwargs:
                self.wokSearch = wok3.WokSearch(kwargs['proxy'])
            else:
                self.wokSearch = wok3.WokSearch()
        
        self.wokSearch.openSOAPsession()
        

        self.wokSearch.setMaxRecords(100)
        self.wokSearch.setFirstRecord(self.retrieved+1)
        self.folder = Path('./')
        self.projectname = 'untilted'
        self.fileindex = 0 
            

        
    def setQuery(self,query,retrieved=0):
        self.wokSearch.setQuery(query)
        self.retrieved = retrieved
        
    def setTimeSpanStart(self,year):
        self.wokSearch.setTimeSpanStart(datetime.date(year,1,1))
        
    def setTimeSpanEnd(self,year):
        self.wokSearch.setTimeSpanEnd(datetime.date(year,12,31))
        
    def setSaveSettings(self,projectFile):
        self.folder = projectFile.parent
        self.projectname = projectFile.stem
        self.fileindex = 0
        while (self.folder / (self.projectname+str(self.fileindex)+'.JSON')).exists():
            self.fileindex += 1  
        
        
    def __del__(self):
        self.wokSearch.closeSOAPsession()
        
    @QtCore.pyqtSlot()   
    def pause(self):
        self.exiting = True
    
    @QtCore.pyqtSlot()    
    def run(self):
        print(self.wokSearch.queryToSOAP())
        print(self.wokSearch.retrieveParamToSOAP())
        while (self.exiting is False) and (self.finished is False):
            resp = self.wokSearch.sendSearchRequest()    
            if self.firstsearch:
                self.total = resp.getNbRecordsFound()
                print(self.total)
                self.totalUpdated.emit(self.total)
                self.firstsearch = False
            self.retrieved += resp.getNbRecordsRetrieved()
            print(self.retrieved)
            self.retrievedUpdated.emit(self.retrieved)
            resp.saveAsJSON(str(self.folder / (self.projectname+str(self.fileindex)+'.JSON')))
            self.fileindex += 1
            if self.retrieved>=self.total:
                self.finished = True
                self.searchFinished.emit()
                print(self.finished)
 
        #multiples search
    
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())