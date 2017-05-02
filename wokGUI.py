import sys
from PyQt4 import QtCore, QtGui, uic
import wok3

qtCreatorFile = "easyWok3.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.pSearchOnce.clicked.connect(self.search)
        self.pStop.clicked.connect(self.stop)
        self.criteriaNb = 0
        self.pAddCriteria.clicked.connect(self.addCriteria)
        
        self.criteriaList = []
        self.addCriteria()
        
        
        with open('proxy.txt', 'r') as fp:
            proxySettings = {}
            proxySettings['login'] = fp.readline()[:-1]
            proxySettings['password'] = fp.readline()[:-1]
            proxySettings['server'] = fp.readline()[:-1]
            proxySettings['port'] = fp.readline()
    
        self.wokSearch = wok3.WokSearch(proxy=dict(http='http://'+proxySettings['login']+':'+proxySettings['password']+'@'+proxySettings['server']+':'+proxySettings['port']))
        self.wokSearch.openSOAPsession()
        
        
    def closeEvent(self, event):
        self.wokSearch.closeSOAPsession()
        
    def search(self):
        searchQuerry = ''
        for (cbCriteria,leCriteria) in self.criteriaList:
            searchQuerry += wok3.WokSearch.CRITERIA[cbCriteria.currentText()]
            searchQuerry += '=('
            searchQuerry += leCriteria.text()
            searchQuerry += ') AND '
        searchQuerry = searchQuerry[:-5]
        print searchQuerry
        self.wokSearch.setQuery(searchQuerry)
        self.querryResp = self.wokSearch.sendSearchRequest()
        self.lRetrieved.setText(str(self.querryResp.getNbRecordsRetrieved()) + '/' +str(self.querryResp.getNbRecordsFound()))

        resultList = self.querryResp.toList()
        if resultList:
            row = len(resultList)
            model = QtGui.QStandardItemModel(row,4)

            model.setHorizontalHeaderItem(0, QtGui.QStandardItem('Year'))
            model.setHorizontalHeaderItem(1, QtGui.QStandardItem('Title'))
            model.setHorizontalHeaderItem(2, QtGui.QStandardItem('Journal'))
            model.setHorizontalHeaderItem(3, QtGui.QStandardItem('First Author'))
  
            j = 0
            for article in resultList:
                model.setItem(j,0, QtGui.QStandardItem(article['year']))
                model.setItem(j,1, QtGui.QStandardItem(article['title']))
                model.setItem(j,2, QtGui.QStandardItem(article['journal']))
                model.setItem(j,3, QtGui.QStandardItem(article['authors'][0]['name']))
                j += 1
                
            self.tvResults.setModel(model)
        
    def stop(self):
        print 'stop'
        
    def addCriteria(self):
        cbCriteria = QtGui.QComboBox()
        cbCriteria.addItems(wok3.WokSearch.CRITERIA.keys())
        leCriteria = QtGui.QLineEdit()
        self.criteriaList.append((cbCriteria,leCriteria))
        self.flCriteria.addRow(cbCriteria,leCriteria) 
        self.centralwidget.setLayout(self.gridLayout)


class SearchThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
 
    def run(self):
        print 1+1        
        return

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())