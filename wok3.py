# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 10:12:00 2014

@author: mathiasstrupler
"""


import sys
import re
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
    
try:
    import xml.etree.ElementTree as ET
except ImportError:
    print('We need ElementTree, sorry...')
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
 
class FieldsSelector(object):
    def __init__(self):
        self._title= True
        self._name= True
   

class WokSearch(object):
    AUTH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
    SEARCH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
    def __init__(self):
        #initialization
        self._queryLanguage = 'en'
        self._databaseId = 'WOS'
        self._timeSpanStart = None
        self._timeSpanEnd = None
        self._edition = None
        self._query = None
        self._resultsRetrieved = 0
        self._resultsPerRequest = 100
    
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
        
    def queryToSOAP(self):
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
    
    def retrieveParamToSOAP(self):
        soap = {'firstRecord' : self._resultsRetrieved+1, 'count' : self._resultsPerRequest}
        return soap
        
    def openSOAPsession(self):
        self._authClient = Client(self.AUTH_URL)
        self._sid = self._authClient.service.authenticate()
        headers = { 'Cookie': 'SID='+self._sid}
        self._authClient.set_options(soapheaders=headers)
        self._searchClient = Client(self.SEARCH_URL, headers= { 'Cookie': 'SID='+self._sid})
    
    def closeSOAPsession(self):
        self._authClient.service.closeSession()
        
    def sendSearchRequest(self):
        resp = self._searchClient.factory.create('searchResponse')
        resp = self._searchClient.service.search(self.queryToSOAP(),self.retrieveParamToSOAP())
        return resp        
        
    def searchRespToDict(self,searchResp):
        ans = {'queryID' : searchResp.queryId, 'recordsFound' : searchResp.recordsFound, 'records' : [] }
        records = re.sub(' xmlns="http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"', '', searchResp.records, count=1)
        #records = re.sub(' r_id_disclaimer="ResearcherID data provided by Thomson Reuters"', '', resp.records, count=resp.recordsFound)
        recordsTree = ET.fromstring( records)
        for rec in recordsTree.iter('REC'):
            #retreive UID
            record = {'UID' : rec.find('UID').text}
            #retreive title and journal name
            for title in rec.findall('static_data/summary/titles/title'):
                if title.attrib['type'] == 'item':
                    record['title'] = title.text
                if title.attrib['type'] == 'source':
                    record['journal'] = title.text
            #retreive publication information 
            record['pubinfo'] = rec.find('static_data/summary/pub_info').attrib
            #retreive author list 
            record['authors'] = []
            for name in rec.findall('static_data/summary/names/name'):
                record['authors'].append(name.find('wos_standard').text)
            #retrieve publication language
                
            #retrieve adressess
                
            #retrieve doctype
                
            #append record to answer
            ans['records'].append(record)
        return ans
            
        
def main():
    wokSearch = WokSearch()
    
    wokSearch.setQuery('AU = Strupler')
   
    wokSearch.setEdition(Edition.SCI)
    wokSearch.setTimeSpanEnd(datetime.date(2010,01,01))
    wokSearch.setTimeSpanStart(datetime.date(2003,01,01))
    print wokSearch.queryToSOAP()
    print wokSearch.retrieveParamToSOAP()
    
    wokSearch.openSOAPsession()
    resp = wokSearch.sendSearchRequest()
    print wokSearch.searchRespToDict(resp)
    wokSearch.closeSOAPsession()
    
if __name__ == "__main__":
    sys.exit(main())    
    