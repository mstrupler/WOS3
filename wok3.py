# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 10:12:00 2014

@author: mathiasstrupler
"""


import sys
import datetime 

#try:
#    import urllib2
#except ImportError:
#    print('We need urllib2, sorry...')
#    sys.exit(1)

try:    
    from suds.client import Client
except ImportError:
    print('We need suds, sorry...')
    sys.exit(1)   
    
class Error(Exception):
    """Base class for any wok3 error."""
    
class SearchQueryError(Error):
    """You need to set a user query"""

class Edition(object):        
    SCI   = {'collection' : 'WOS', 'edition' : 'SCI'}    #Science Citation Index Expanded
    SSCI  = {'collection' : 'WOS', 'edition' : 'SSCI'}   #Social Sciences Citation Index
    AHCI  = {'collection' : 'WOS', 'edition' : 'AHCI'}   #Arts & Humanities Citation Index
    ISTP  = {'collection' : 'WOS', 'edition' : 'ISTP'}   #Conference Proceedings Citation Index - Science
    ISSHP = {'collection' : 'WOS', 'edition' : 'ISSHP'}  #Conference Proceedings Citation Index - Social Sciences
    IC    = {'collection' : 'WOS', 'edition' : 'IC'}     #Index Chemicus
    CCR   = {'collection' : 'WOS', 'edition' : 'CCR'}    #Current Chemical Reactions
    BSCI  = {'collection' : 'WOS', 'edition' : 'BSCI'}   #Book Citation Index - Science
    BHCI  = {'collection' : 'WOS', 'edition' : 'BHCI'}   #Book Citation Index - Social Sciences and Humanities
   

class WokSearch(object):
    def __init__(self):
        #initialization
        self._queryLanguage = 'en'
        self._databaseId = 'WOS'
        self._timeSpanStart = None
        self._timeSpanEnd = None
        self._edition = None
        self._query = None
    
    def setQuery(self, query):
        self._query = query
        
    def setEdition(self, edition):
        self._edition = edition
    
    def setTimeSpanStart(self, date):
        self._timeSpanStart = date
        
    def setTimeSpanEnd(self, date):
        self._timeSpanEnd = date
        
    def clearEdition(self):
        self._edition = None
    
    def clearSpanTime(self):
        self._timeSpanStart = None
        self._timeSpanEnd = None
        
    def toSOAP(self):
        if self._query is not None:
            soap =  {'databaseId' : self._databaseId, 'userQuery' : self._query, 'queryLanguage': self._queryLanguage}
            if self._edition is not None:
                soap['editions'] = self._edition
            soaptime = {}
            if self._timeSpanStart is not None:
                soaptime['begin'] = self._timeSpanStart.isoformat()
            if self._timeSpanEnd is not None:
                soaptime['end'] = self._timeSpanEnd.isoformat()
            if soaptime :    
                soap['timeSpan'] = soaptime     
            return soap
        else:
            raise SearchQueryError
        
def main():
    wokSearch = WokSearch()
    
    wokSearch.setQuery('AU = (Strupler AND Boudoux)')
    print wokSearch.toSOAP()
    wokSearch.setEdition(Edition.SCI)
    wokSearch.setTimeSpanEnd(datetime.date(2010,01,01))
    wokSearch.setTimeSpanStart(datetime.date(2003,01,01))
    
    
if __name__ == "__main__":
    sys.exit(main())    
    