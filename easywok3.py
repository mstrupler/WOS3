# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 14:57:48 2015

@author: mathiasstrupler
"""

from wok3 import WokSearch as WS

class EWsearch(object):
    def __init__(self,resultFileName, resutlFileType = 'JSON' ):
        #initialization
        self._ws = WS()
        self._done = False
        self._started = False
        self._retrieved= 0
        self._toRetrieve = 0
        self._queryDelay = 1
        self._file = resultFileName
        self._filetype = resutlFileType
        self._openedSession = False
        
    def setQuery(self,query):
        self._ws.setQuery(query)
        
    def search():
        if not self._openedSession:
            self._ws.openSOAPsession()
            
        resp = self._ws.sendSearchRequest()
        
        if not self._started:
            self._started = True
            self._toRetrieve = resp.getNbRecordsFound()
            self._retrieved = resp.getNbRecordsRetrieved()    
        else:
            self._retrieved = self._retrieved + resp.getNbRecordsRetrieved()
            if self._retrieved>= self._toRetrieve:
                self._done = True
            else:
                
                self.search()
        
        
        

ws = EWsearch()
ws.setQuery('TS = Optical Coherence Tomography')
ws.openSOAPsession()
resp = ws.sendSearchRequest()
print 'Search found ', resp.getNbRecordsFound(), ' matching records'
print 'Search retrieved ', resp.getNbRecordsRetrieved(), ' records'

