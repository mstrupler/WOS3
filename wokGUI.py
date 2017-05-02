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
        self.pSearch.clicked.connect(self.search)
        self.pStop.clicked.connect(self.stop)
        self.eTopic.editingFinished.connect(self.setQuerryTopic)
        
        with open('proxy.txt', 'r') as fp:
            proxySettings = {}
            proxySettings['login'] = fp.readline()[:-1]
            proxySettings['password'] = fp.readline()[:-1]
            proxySettings['server'] = fp.readline()[:-1]
            proxySettings['port'] = fp.readline()
    
        self.wokSearch = wok3.WokSearch(proxy=dict(http='http://'+proxySettings['login']+':'+proxySettings['password']+'@'+proxySettings['server']+':'+proxySettings['port']))
        self.wokSearch.openSOAPsession()
        
    def setQuerryTopic(self):
        self.wokSearch.setQuery('TS = '+self.eTopic.text())
        
    def closeEvent(self, event):
        self.wokSearch.closeSOAPsession()
        
    def search(self):
        self.querryResp = self.wokSearch.sendSearchRequest()
        self.lRetrieved.setText(str(self.querryResp.getNbRecordsRetrieved()) + '/' +str(self.querryResp.getNbRecordsFound()))
        
    def stop(self):
        print 'stop'

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