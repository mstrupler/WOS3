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
    print('We need suds.client, sorry...')
    sys.exit(1)   
    
try:
    import xml.etree.ElementTree as ET
except ImportError:
    print('We need xml.etree.ElementTree, sorry...')
    sys.exit(1)  

class Error(Exception):
    """Base class for any wok3 error."""
    
class SearchQueryError(Error):
    """You need to set a user query"""

class Edition(object):    
    """
    This class is only used to let you know easily all the databases 
    that can be searched in World of sciences
    example : wokSearch.setEdition(Edition.SCI)
    """    
    SCI   = {'collection' : 'WOS', 'edition' : 'SCI'}    #Science Citation Index Expanded
    SSCI  = {'collection' : 'WOS', 'edition' : 'SSCI'}   #Social Sciences Citation Index
    AHCI  = {'collection' : 'WOS', 'edition' : 'AHCI'}   #Arts & Humanities Citation Index
    ISTP  = {'collection' : 'WOS', 'edition' : 'ISTP'}   #Conference Proceedings Citation Index - Science
    ISSHP = {'collection' : 'WOS', 'edition' : 'ISSHP'}  #Conference Proceedings Citation Index - Social Sciences
    IC    = {'collection' : 'WOS', 'edition' : 'IC'}     #Index Chemicus
    CCR   = {'collection' : 'WOS', 'edition' : 'CCR'}    #Current Chemical Reactions
    BSCI  = {'collection' : 'WOS', 'edition' : 'BSCI'}   #Book Citation Index - Science
    BHCI  = {'collection' : 'WOS', 'edition' : 'BHCI'}   #Book Citation Index - Social Sciences and Humanities
 
        
class SearchRespAnalyzer(object): 
    """
    This class is used to parse the soap answer received 
    after a search request
    """    
    def __init__(self,searchResp= None):
        """
        Initialization of the class 
        @type searchResp:
        @param searchResp: raw xml response obtained form a SOAP query 
        """
        if searchResp == None:
            self._rawResp = None
        else:
            self._rawResp = searchResp
        self.recordsTree = None
        
    def createRecordTree(self):
        records = re.sub(' xmlns="http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"', '', self._rawResp.records, count=1)
 
        #records = re.sub(' r_id_disclaimer="ResearcherID data provided by Thomson Reuters"', '', resp.records, count=resp.recordsFound)
        #parser = ET.XMLParser(encoding='utf-8') 
        self.recordsTree = ET.fromstring(records)
            
    def getQueryId(self):
        """
        This methods return the number of matching records found
        """
        return self._rawResp.queryId
        
    def getNbRecordsSearched(self):
        """
        This methods return the number of records searched (size of the Databas)
        """
        return self._rawResp.recordsSearched
        
    def getNbRecordsFound(self):
        """
        This methods return the number of records found that satisfy this query
        """
        return self._rawResp.recordsFound
        
    def getNbRecordsRetrieved(self):
        """
        This methods return the number of retrieved records found
        """
        if self.recordsTree is None:      
            self.createRecordTree()
        return len(self.recordsTree.findall('REC'))
        
    
    def toList(self):
        """
        This method parse the answer into a dictonnary
        It does not retreive all the information that gives WOS 
        It looks for the following info:
            UID : WOS identifier
            title : Title of the document
            journal : Name of the journal 
            year : Year of publication
            volume : Volume
            issue : Issue
            page : page [begin, end]
            authors : list of author dict {name, dais_id, affiliations list}
            language : primary language of the document
            docType : document type (article, review, book,...)
            publisher : name of the publisher
        """  

        ans = []
        if self.recordsTree is None:      
            self.createRecordTree()
            
        for rec in self.recordsTree.iter('REC'):
            #retreive UID
            record = {'UID' : rec.find('UID').text}
            #retreive title and journal name
            record['title'] = None
            record['journal'] = None
            for title in rec.findall('static_data/summary/titles/title'):
                if title.attrib['type'] == 'item':
                    record['title'] = title.text
                if title.attrib['type'] == 'source':
                    record['journal'] = title.text
            #retreive publication information 
            pubinfo = rec.find('static_data/summary/pub_info').attrib
            if 'pubyear' in pubinfo:
                record['year'] = pubinfo['pubyear']
            else:
                record['year'] = ''
                
            if 'vol' in pubinfo:
                record['volume'] = pubinfo['vol']
            else:
                record['volume'] = ''
                
            if 'issue' in  pubinfo:
                record['issue'] = pubinfo['issue']
            else:
                record['issue'] = ''
                
            page = rec.find('static_data/summary/pub_info/page').attrib
            if 'begin' in  page:
                record['page'] = [page['begin'],page['end']]
            else:
                record['page'] = []
            #retreive author list 
            record['authors'] = []
            for name in rec.findall('static_data/summary/names/name'):
                if name.attrib['role']=='author':
                    author = {'name' : ''}
                    if name.find('wos_standard') is not None:
                        author['name'] = name.find('wos_standard').text
                    elif name.find('display_name') is not None:
                        author['name'] = name.find('display_name').text
                    elif name.find('full_name') is not None:
                        author['name'] = name.find('full_name').text
                    if 'dais_id' in name.attrib:
                        author['dais_id'] = name.attrib['dais_id'] 
                    author['affiliation']=[]
                    record['authors'].append(author)
            #retrieve publication language
            record['language'] = None
            for language in rec.findall('static_data/fullrecord_metadata/languages/language'):    
                if language.attrib['type']=='primary':
                    record['language'] = language.text
            #retrieve adressess
            affiliations = []
            for adresses in rec.findall('static_data/fullrecord_metadata/addresses/address_name'):
                affiliations.append({'nb' : adresses.find('address_spec').attrib['addr_no'],'add' : adresses.find('address_spec/full_address').text})
            record['affiliations'] = affiliations
            if len(affiliations)==1:
                for author in record['authors']:
                    author['affiliation']=[affiliations[0]['add']]
            if len(affiliations)>=1:
                aff_names = rec.findall('static_data/fullrecord_metadata/addresses/address_name/names/name')
                aff_names_list = []                
                for aff_name in aff_names:
                    tmp = {'nb' : aff_name.attrib['addr_no'], 'name' : aff_name.find('wos_standard').text}
                    aff_names_list.append(tmp)    
                for author in record['authors']:
                    for name in aff_names_list:
                        if author['name'] == name['name']:                            
                            author['affiliation'].append(name['nb'])
                                    
            #retrieve doctype
            record['docType'] = []
            for docType in rec.findall('static_data/fullrecord_metadata/normalized_doctypes/doctype'):
                record['docType'].append(docType.text)  
            #retrieve publisher
            record['publisher'] = rec.find('static_data/summary/publishers/publisher/names/name/full_name').text
            
            #append record to answer
            ans.append(record)
        return ans
        
    def toDict(self):
        """
        This methods return a dictionnary containning all the records retreived by the search
        """
        return {'records':self.toList()}

    def saveAsJSON(self,filename):
        """
        This method save as a JSON file 
        the dictionnary produced by the toDict() method
        """   
        try:
            import json
        except ImportError:
            print('We need JSON, sorry...')
            sys.exit(1)  
        
        with open(filename, 'w', encoding="utf8") as fp:
            json.dump(self.toDict() , fp, sort_keys=True, indent=4, separators=(',', ': '))
            
    def saveRawAsXML(self,filename):
        """
        This method save as a XML file the raw records 
        returned by the WOS search
        It only adds identations to make it more prettier
        """  
        
        #from xml.dom import minidom

        if self.recordsTree is None:      
            self.createRecordTree()
        tree = ET.ElementTree(self.recordsTree)   
        with open(filename, 'w', encoding='utf-8') as file:
            tree.write(file, encoding='unicode')
        #rough_string = ET.tostring(self.recordsTree, 'utf-8')
        #reparsed = minidom.parseString(rough_string)
        #with open(filename, 'wb') as fp:
        #    reparsed.writexml(fp, indent="", addindent="\t", newl="\n")


    def saveToStreamAsBibtex(self,outputstream):
        """
        This method save as a bibtex file the results list produced by the toList() method
        Note that I reduced the docType to @article, @proceedings, @book, @inbook and @misc
        Note that the results UID is used as citstion-key
        Note that only the following info are kept for the bibtex entry: title, authors, journal, volume, issue, pages, year and publisher
        
        TODO : improve different doctype handling        
        """  
        for rec in self.toList():
                if rec['docType'][0]=='Article' or rec['docType'][0]=='Review' or rec['docType'][0]=='Letter':
                    bibtexentry = '@article{'
                elif rec['docType'][0]=='Proceedings Paper' or rec['docType'][0]=='Meeting':
                    bibtexentry = '@proceedings{'
                elif rec['docType'][0]=='Book':
                    bibtexentry = '@book{'
                elif rec['docType'][0]=='Book Chapter':
                    bibtexentry = '@inbook{'
                else:
                    bibtexentry = '@misc{'
                bibtexentry = bibtexentry + rec['UID'] + ',\n' 
                bibtexentry = bibtexentry + '  title={' + rec['title'] + '},\n'
                
                authors = ''
                authorlist = rec['authors']
                firstauthor = authorlist.pop(0)
                authors = firstauthor['name']
                for author in authorlist:
                    authors = authors + ' and ' + author['name']
                    
                bibtexentry = bibtexentry + '  author={' + authors + '},\n'
                bibtexentry = bibtexentry + '  journal={' + rec['journal'] + '},\n'
                if not(rec['volume']==''):
                    bibtexentry = bibtexentry + '  volume={' + rec['volume'] + '},\n'
                if not(rec['issue']==''):
                    bibtexentry = bibtexentry + '  number={' + rec['issue'] + '},\n'
                if rec['page']:
                    bibtexentry = bibtexentry + '  pages={'  + rec['page'][0] + '--' + rec['page'][1] + '},\n'
                if not(rec['year']==''):
                    bibtexentry = bibtexentry + '  year={' + rec['year'] + '},\n'
                if not(rec['publisher']==''):
                    bibtexentry = bibtexentry + '  publisher={' + rec['publisher'] + '},\n'
                bibtexentry = bibtexentry  + '}\n'
                outputstream.write(bibtexentry)
    
    def saveToFileAsBibtex(self,filename):
        """
        This method save as a bibtex files all the records
        It should be rewritten better handle different document types 
        """  
        
        with open(filename, 'w') as fp:
            self.saveToStreamAsBibtex(fp)
        
        
        
        
   

class WokSearch(object):
    """
    This class is used 
        - to define the query parameters of a WOK search 
        - open a session on WOK 
        - send requests
        - close the session
    
    """
    AUTH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
    SEARCH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
    CRITERIA = {'Address':'AD',\
                'Author':'AU',\
                'Conference':'CF',\
                'City':'CI',\
                'Country':'CU',\
                'DOI':'DO',\
                'Editor':'ED',\
                'Grant number':'FG',\
                'Funding agency':'FO',\
                'Funding Text':'FT',\
                'Group Author':'GP',\
                'ISSN/ISBN':'IS',\
                'Organization - Enhanced':'OG',\
                'Organization':'OO',\
                'Province/State':'PS',\
                'Year published':'PY',\
                'Researcher ID':'RID',\
                'Street address':'SA',\
                'Suborganization':'SG',\
                'Publication name':'SO',\
                'Research area':'SU',\
                'Title':'TI',\
                'Topic':'TS',\
                'Accession number':'UT',\
                'Web of science category':'WC',\
                'Zip/Postal Code':'ZP'}
    SEARCH_OPERATOR = ['AND', 'OR', 'NOT', 'NEAR', 'SAME']
    def __init__(self,**kwargs):
        """
            initialize the search to default values
            kwargs are : 
             - language: search language (it seems taht it can only be en foe english)
             - database: searched database, see possible value in class Edition
             - timeStart: defines the begining of the time range of publication dates
             - timeEnd: defines the end of the time range
             - edition: defines the search databases see class Edition
             - query: the search query
             - maxRec: maximum number of results to retrieve (max 100)
             - firstRec : defines the record position at with the results should start (used in the case the number of results is higher than maxRec)
             - proxy: proxy settings (http://login:password@server_url:port)
        """
        self._queryLanguage = 'en'
        self._databaseId = 'WOS'
        self._timeSpanStart = None
        self._timeSpanEnd = None
        self._edition = None
        self._query = None
        self._firstRecord = 1
        self._resultsPerRequest = 100
        if kwargs is not None: 
            if 'language' in kwargs:
                self._queryLanguage = kwargs['language']
            if 'database' in kwargs:
                self._databaseId = kwargs['database']
            if 'timeStart' in kwargs:
                self._timeSpanStart = kwargs['timeStart']
            if 'timeEnd' in kwargs:
                self._timeSpanEnd = kwargs['timeEnd']
            if 'edition' in kwargs:
                self._edition = kwargs['edition']
            if 'query' in kwargs:
                self._query = kwargs['query']
            if 'firstRec' in kwargs:
                self._firstRecord = kwargs['firstRec']
            if 'maxRec' in kwargs:
                self._resultsPerRequest = kwargs['maxRec'] 
            if 'proxy' in kwargs:
                self._proxySettings = kwargs['proxy']                  

    
    def setQuery(self, query):
        """
            Sets the query
            @type query: String
            @param query: The search query (ex: "TS=Mars AND rover")
        """
        self._query = query
        
    def getQuery(self):
        """
            get current the query
            @rtype : String
            @rparam : The search query (ex: "TS=Mars AND rover")
        """
        return self._query
        
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
        
    def setMaxRecords(self,numberOfRecordsToRetrieve):
        self._resultsPerRequest = numberOfRecordsToRetrieve
        
    def setFirstRecord(self,indexOfFirstRecordToRetrieve):
        self._firstRecord = indexOfFirstRecordToRetrieve
        
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
        soap = {'firstRecord' : self._firstRecord, 'count' : self._resultsPerRequest}
        return soap
        
    def openSOAPsession(self):
        if self._proxySettings:
            self._authClient = Client(self.AUTH_URL,proxy=self._proxySettings)
        else:
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
        analyzedResp = SearchRespAnalyzer(resp)
        return analyzedResp        
        
            
        
def main():
    with open('proxy.txt', 'r') as fp:
        proxySettings = {}
        proxySettings['login'] = fp.readline()[:-1]
        proxySettings['password'] = fp.readline()[:-1]
        proxySettings['server'] = fp.readline()[:-1]
        proxySettings['port'] = fp.readline()
    
    wokSearch = WokSearch(proxy=dict(http='http://'+proxySettings['login']+':'+proxySettings['password']+'@'+proxySettings['server']+':'+proxySettings['port']))
    
    #wokSearch.setQuery('TS = Optical Coherence Tomography')
    wokSearch.setQuery('AU = Bouma B*')
    #wokSearch.setEdition(Edition.SCI)
    #wokSearch.setTimeSpanEnd(datetime.date(2014,01,01))
    #wokSearch.setTimeSpanStart(datetime.date(2003,01,01))
    wokSearch.setMaxRecords(3)
    wokSearch.setFirstRecord(457)
    print(wokSearch.queryToSOAP())
    print(wokSearch.retrieveParamToSOAP())
    
    wokSearch.openSOAPsession()
    resp = wokSearch.sendSearchRequest()
    
    
    print('Search found ' + str(resp.getNbRecordsFound()) + ' matching records')
    print('Search retrieved ' + str(resp.getNbRecordsRetrieved()) + ' records')
    resp.saveRawAsXML('/Users/mathiasstrupler/Documents/code/python/WOS3/bouma_raw.xml')
    resp.saveAsJSON('/Users/mathiasstrupler/Documents/code/python/WOS3/bouma.JSON')
    resp.saveToFileAsBibtex('/Users/mathiasstrupler/Documents/code/python/WOS3/bouma.bib')
    wokSearch.closeSOAPsession()
    
if __name__ == "__main__":
    sys.exit(main())    
    