# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 10:30:33 2014

@author: mathiasstrupler
"""


import sys
import time
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
    
class TimeSpan(object):
    def __init__(self, begin = None, end = datetime.date.today()):
        self.begin = begin
        self.end = end
        
    def setBegin(self,date):
        self.begin = date
    
    def setEnd(self,date):
        self.end = date
    
    def wok(self):
        woktimeSpan = {'end' : self.end.isoformat()}
        if self.begin is not None:
            woktimeSpan['begin'] = self.begin
        return woktimeSpan 
        
class Editions(object):        
    SCI   = {'collection' : 'WOS', 'edition' : 'SCI'}    #Science Citation Index Expanded
    SSCI  = {'collection' : 'WOS', 'edition' : 'SSCI'}   #Social Sciences Citation Index
    AHCI  = {'collection' : 'WOS', 'edition' : 'AHCI'}   #Arts & Humanities Citation Index
    ISTP  = {'collection' : 'WOS', 'edition' : 'ISTP'}   #Conference Proceedings Citation Index - Science
    ISSHP = {'collection' : 'WOS', 'edition' : 'ISSHP'}  #Conference Proceedings Citation Index - Social Sciences
    IC    = {'collection' : 'WOS', 'edition' : 'IC'}     #Index Chemicus
    CCR   = {'collection' : 'WOS', 'edition' : 'CCR'}    #Current Chemical Reactions
    BSCI  = {'collection' : 'WOS', 'edition' : 'BSCI'}   #Book Citation Index - Science
    BHCI  = {'collection' : 'WOS', 'edition' : 'BHCI'}   #Book Citation Index - Social Sciences and Humanities
   
class SortFields(object):        
    def __init__(self):
        self.name="RS"
        self.descending=True
    
    def sortbyAuthor(self,descending = True):
        self.name="AU"
        self.descending = descending
    
    def sortbyPublicationYear(self,descending = True):
        self.name="PY"
        self.descending = descending
        
    def sortbyTimeCited(self):
        self.name="TC"
        self.descending = True
    
    def sortbyRelevance(self):
        self.name="RS"
        self.descending = True
        
    def wok(self):
        wokSortField = {'name':self.name}
        if self.descending :
            wokSortField['sort']='D'
        else:
            wokSortField['sort']='A'
             
    
class QueryParameters(object):
    def __init__(self, query, timeSpan = None, editions = None):
        self.queryLanguage = 'en'
        self.databaseId = 'WOS'
        self.timeSpan = timeSpan
        #self.symbolicTimeSpan 
        self.editions = editions
        self.userQuery = query
        
    def setTimeSpan(self,begin,end):
        self.timeSpan.setBegin(begin)
        self.timeSpan.setEnd(end)
    
    def setEditions(self,editions):
        self.editions = editions
    
    def setQuery(self,query):
        self.userQuery = query
    
    def wok(self):
        wokquery =  {'databaseId' : self.databaseId, 'userQuery' : self.userQuery, 'queryLanguage': self.queryLanguage}
        if self.editions is not None:
            wokquery['editions'] = self.editions
        if self.timeSpan is not None:
            wokquery['timeSpan'] =  self.timeSpan.wok(),   
        return wokquery

class RetrieveParameters(object):   
    def __init__(self, firstRecord = 1, count = 100, sortField = [], viewField = [], option=[]):
        self.firstRecord = firstRecord
        self.count = count
        self.sortField = sortField
        self.option = option
    
    
class WokAuth(object):
    URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
    #Methods (2):
    #   authenticate()
    #   closeSession()
    #Types (10):    
    #   AuthenticationException
    #   ESTIWSException
    #   InternalServerException
    #   InvalidInputException
    #   QueryException
    #   SessionException
    #   authenticate
    #   authenticateResponse
    #   closeSession
    #   closeSessionResponse
    def __init__(self):
        self.client = Client(self.URL)
    
    def authenticate(self):
        self.identifier = self.client.service.authenticate()
        headers = { 'Cookie': 'SID='+self.identifier}
        self.client.set_options(soapheaders=headers)
        return self.identifier
    
    def closeSession(self):
        self.client.service.closeSession()

class WokSearch(object):
    URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
    #Service ( WokSearchService ) tns="http://woksearch.v3.wokmws.thomsonreuters.com"
    #Prefixes (1)
    #   ns0 = "http://woksearch.v3.wokmws.thomsonreuters.com"
    #Ports (1):
    #  (WokSearchPort)
    #   Methods (7):
    #       citedReferences(xs:string databaseId, xs:string uid, xs:string queryLanguage, retrieveParameters retrieveParameters, )
    #       citedReferencesRetrieve(xs:string queryId, retrieveParameters retrieveParameters, )
    #       citingArticles(xs:string databaseId, xs:string uid, editionDesc[] editions, timeSpan timeSpan, xs:string queryLanguage, retrieveParameters retrieveParameters, )
    #       relatedRecords(xs:string databaseId, xs:string uid, editionDesc[] editions, timeSpan timeSpan, xs:string queryLanguage, retrieveParameters retrieveParameters, )
    #       retrieve(xs:string queryId, retrieveParameters retrieveParameters, )
    #       retrieveById(xs:string databaseId, xs:string[] uid, xs:string queryLanguage, retrieveParameters retrieveParameters, )
    #       search(queryParameters queryParameters, retrieveParameters retrieveParameters, )
    #   Types (35):
    #       AuthenticationException
    #       ESTIWSException
    #       FaultInformation
    #       InternalServerException
    #       InvalidInputException
    #       QueryException
    #       RawFaultInformation
    #       SessionException
    #       SupportingWebServiceException
    #       citedReference
    #       citedReferences
    #       citedReferencesResponse
    #       citedReferencesRetrieve
    #       citedReferencesRetrieveResponse
    #       citedReferencesSearchResults
    #       citingArticles
    #       citingArticlesResponse
    #       editionDesc
    #       fullRecordData
    #       fullRecordSearchResults
    #       keyValuePair
    #       labelValuesPair
    #       queryParameters
    #       relatedRecords
    #       relatedRecordsResponse
    #       retrieve
    #       retrieveById
    #       retrieveByIdResponse
    #       retrieveParameters
    #       retrieveResponse
    #       search
    #       searchResponse
    #       sortField
    #       timeSpan
    #       viewField
    def __init__(self,identifier):
        self.client = Client(self.URL, headers= { 'Cookie': 'SID='+identifier})
        
    def queryParameters(self):
        print self.client.factory.create('viewField')
        
    
        

def main():
    
    query = QueryParameters("AU = Strupler") 
    print query.wok()
    auth = WokAuth()
    identifier = auth.authenticate()
    search = WokSearch(identifier)
    print search.queryParameters()
    auth.closeSession()
 


     
if __name__ == "__main__":
    sys.exit(main())