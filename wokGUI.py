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
        self.pSearchAll.clicked.connect(self.searchAll)
   
        self.criteriaNb = 0
        self.pAddCriteria.clicked.connect(self.addCriteria)
        
        self.criteriaList = []
        self.addCriteria()
        
        self.createQuery()
        
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
        
    def createQuery(self):
        self.searchQuery = ''
        for (cbCriteria,leCriteria) in self.criteriaList:
            self.searchQuery += wok3.WokSearch.CRITERIA[cbCriteria.currentText()]
            self.searchQuery += '=('
            self.searchQuery += leCriteria.text()
            self.searchQuery += ') AND '
        self.searchQuery = self.searchQuery[:-5]
        self.lSearchQuery.setText('Query: '+ self.searchQuery)
        
    def search(self):
        self.wokSearch.setQuery(self.searchQuery)
        self.queryResp = self.wokSearch.sendSearchRequest()
        self.lRetrieved.setText(str(self.queryResp.getNbRecordsRetrieved()) + '/' +str(self.queryResp.getNbRecordsFound()))

        resultList = self.queryResp.toList()
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
        

        
    def addCriteria(self):
        cbCriteria = QtGui.QComboBox()
        cbCriteria.addItems(list(wok3.WokSearch.CRITERIA))
        leCriteria = QtGui.QLineEdit()
        self.criteriaList.append((cbCriteria,leCriteria))
        self.flCriteria.addRow(cbCriteria,leCriteria) 
        self.tabSearch.setLayout(self.vlSearch)
        
        cbCriteria.currentIndexChanged.connect(self.createQuery)
        leCriteria.editingFinished.connect(self.createQuery)
        
    def searchAll(self):
        self.wokSearch.setQuery(self.searchQuery)
        self.queryResp = self.wokSearch.sendSearchRequest()
        retrieved = self.queryResp.getNbRecordsRetrieved()
        totalRetrieved = retrieved
        totalResults = self.queryResp.getNbRecordsFound()
        self.lRetrieved.setText(str(totalRetrieved) + '/' +str(totalResults))
        
        if totalResults>0:
            resultList = self.queryResp.toList()
            model = QtGui.QStandardItemModel(totalResults,4)
            model.setHorizontalHeaderItem(0, QtGui.QStandardItem('Year'))
            model.setHorizontalHeaderItem(1, QtGui.QStandardItem('Title'))
            model.setHorizontalHeaderItem(2, QtGui.QStandardItem('Journal'))
            model.setHorizontalHeaderItem(3, QtGui.QStandardItem('First Author'))  
            articleNb = 0
            for article in resultList:
                model.setItem(articleNb,0, QtGui.QStandardItem(article['year']))
                model.setItem(articleNb,1, QtGui.QStandardItem(article['title']))
                model.setItem(articleNb,2, QtGui.QStandardItem(article['journal']))
                model.setItem(articleNb,3, QtGui.QStandardItem(article['authors'][0]['name']))
                articleNb += 1
            print(totalRetrieved)
            while totalRetrieved <totalResults:
                self.wokSearch.setFirstRecord(totalRetrieved + 1)
                self.queryResp = self.wokSearch.sendSearchRequest()
                retrieved = self.queryResp.getNbRecordsRetrieved()
                totalRetrieved += retrieved
                print(totalRetrieved)
                self.lRetrieved.setText(str(totalRetrieved) + '/' +str(totalResults))
                if retrieved>0:
                    resultList = self.queryResp.toList()
                    for article in resultList:
                        model.setItem(articleNb,0, QtGui.QStandardItem(article['year']))
                        model.setItem(articleNb,1, QtGui.QStandardItem(article['title']))
                        model.setItem(articleNb,2, QtGui.QStandardItem(article['journal']))
                        model.setItem(articleNb,3, QtGui.QStandardItem(article['authors'][0]['name']))
                        articleNb += 1
            self.tvResults.setModel(model)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())