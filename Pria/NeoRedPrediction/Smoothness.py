#!/usr/bin/python
# -*- coding: utf-8 -*-


from gensim import corpora
import operator
import util
import Constants
import os
import json
import math
from numpy import zeros
import numpy as np
from time import time

def printNormalRankedDocs(smoothness, usedTestFiles):
    result = False
    try:
        testScore = smoothness.sum(axis=1)
        testMapping = {}
        for files in range(len(usedTestFiles)):
            testMapping[usedTestFiles[files]] = testScore[files] 
        sorted_x = sorted(testMapping.items(), key=operator.itemgetter(1), reverse=True)
        todayDateFolder = util.getTodayDateFolder()
        write_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.ENGINE_DIR,
                                       todayDateFolder, Constants.GOOGLENEWS)
        if not os.path.exists(write_directory):
                os.makedirs(write_directory)
        outfile = open(os.path.join(write_directory,Constants.SMOOTHNESS_FILE), 'w')
        json_write = {}
        count = 1
        for (key,val) in sorted_x:
            json_write[key] = count
            count = count + 1
        json.dump(json_write, outfile)
        outfile.close()
        result = True
    except Exception, e:
        util.logger.eror("Exception at printing Smoothness Google docs for data : %s" % write_directory)
    return result

def printSuggRankedDocs(smoothness, usedTestFiles):
    result = False
    try:
        testScore = smoothness.sum(axis=1)
        testMapping = {}
        for files in range(len(usedTestFiles)):
            testMapping[usedTestFiles[files]] = testScore[files] 
        sorted_x = sorted(testMapping.items(), key=operator.itemgetter(1), reverse=True)
        todayDateFolder = util.getTodayDateFolder()
        write_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.ENGINE_DIR,
                                       todayDateFolder, Constants.SUGG_GOOGLENEWS)
        if not os.path.exists(write_directory):
                os.makedirs(write_directory)
        outfile = open(os.path.join(write_directory,Constants.SMOOTHNESS_FILE), 'w')
        json_write = {}
        count = 1
        for (key,val) in sorted_x:
            json_write[key] = count
            count = count + 1
        json.dump(json_write, outfile)
        outfile.close()
        result = True
    except Exception, e:
        util.logger.eror("Exception at printing Smoothness GoogleSugg docs for data : %s" % write_directory)
    return result

def Smoothness():
    todayDate = util.getYesterdayDateFolder()
    lastSmoothnessDate = util.loadSettings(Constants.LAST_SMOOTHNESS_DIR)
    lastSuggSmoothnessDate = util.loadSettings(Constants.LAST_SUGG_SMOOTHNESS_DIR)
    
    if lastSmoothnessDate:
        util.logger.info("Google Smoothness done last for ="+lastSmoothnessDate)
    else:
        util.logger.info("Google Smoothness done last for none")
        
    if lastSuggSmoothnessDate:
        util.logger.info("Sugg Google Smoothness done last for ="+lastSuggSmoothnessDate)
    else:
        util.logger.info("Sugg Google Smoothness done last for none")    
        
    if todayDate == lastSmoothnessDate and todayDate ==  lastSuggSmoothnessDate:
        util.logger.info("Smoothness signal done for today" + todayDate)
        return True
    
    
    trainFiles = util.findTrainingFiles()
    trainFiles = util.random_select(trainFiles)
    trainCorpus, usedTrainFiles = util.findCorpus(trainFiles)
    bm25obj = Bm25(trainCorpus)
    trainUniqueWords = []
    for trainText in trainCorpus:
        trainUniqueWords.append(set(trainText))
        
    
    
    normalSmoothness = True
    if todayDate != lastSmoothnessDate:    
        testFiles = util.findTestFiles()
        testCorpus, usedTestFiles = util.findCorpus(testFiles)   
        testJson = {}
        testUniqueWords = []
        smoothness=zeros((len(testCorpus),len(trainCorpus)))
        for testText in testCorpus:
            testUniqueWords.append(set(testText))
        for testDoc in range(len(testCorpus)):
            uniqueTest = testUniqueWords[testDoc]
            SminusDcontext=zeros(bm25obj.N)
            DminusScontext=zeros(bm25obj.N)
            for trainDoc in range(len(trainCorpus)):
                uniqueTrain = trainUniqueWords[trainDoc]
           #     t0 = time()
                SminusD = [word for word in trainCorpus[trainDoc] if word not in uniqueTest]
            #    t1 = time()
                #print "time 1 = "+str(t1-t0)
                DminusS = [word for word in testCorpus[testDoc] if word not in uniqueTrain]
            #    t2 = time()
         #       print "time 2 = "+str(t2-t1)
                SminusDcontext = bm25obj.BM25Score(SminusD)
            #    t3 = time()
          #      print "time 3 = "+str(t3-t2)
                DminusScontext = bm25obj.BM25Score(DminusS)
            #    t4 = time()
          #      print "time 4 = "+str(t4-t3)
                smoothness[testDoc][trainDoc]=np.dot(SminusDcontext,DminusScontext)
          #      t5 = time()
                #print "time 5 = "+str(t5-t4)
        normalSmoothness = printNormalRankedDocs(smoothness, usedTestFiles)
        if normalSmoothness == True:
            util.saveSettings(Constants.LAST_SMOOTHNESS_DIR, todayDate)
            util.logger.info("Google Smoothness info just completed for ="+todayDate)
            
    suggSmoothness = True
    if todayDate != lastSuggSmoothnessDate:    
        testFiles = util.findSuggTestFiles()
        testCorpus, usedTestFiles = util.findCorpus(testFiles)   
        testJson = {}
        testUniqueWords = []
        smoothness=zeros((len(testCorpus),len(trainCorpus)))
        for testText in testCorpus:
            testUniqueWords.append(set(testText))
        for testDoc in range(len(testCorpus)):
            uniqueTest = testUniqueWords[testDoc]
            SminusDcontext=zeros(bm25obj.N)
            DminusScontext=zeros(bm25obj.N)
            for trainDoc in range(len(trainCorpus)):
                uniqueTrain = trainUniqueWords[trainDoc]
                SminusD = [word for word in trainCorpus[trainDoc] if word not in uniqueTest]
                DminusS = [word for word in testCorpus[testDoc] if word not in uniqueTrain]
                SminusDcontext = bm25obj.BM25Score(SminusD)
                DminusScontext = bm25obj.BM25Score(DminusS)
                smoothness[testDoc][trainDoc]=np.dot(SminusDcontext,DminusScontext)
        suggSmoothness = printSuggRankedDocs(smoothness, usedTestFiles)
        if suggSmoothness == True:
            util.saveSettings(Constants.LAST_SUGG_SMOOTHNESS_DIR, todayDate)
            util.logger.info("Sugg Smoothness info just completed for ="+todayDate)
    
    
            
    return normalSmoothness or suggSmoothness

class Bm25:
    
    def __init__(self, fn_docs) :
        self.fn_docs = fn_docs
        self.N = len(fn_docs)
        self.DocAvgLen = 0
        self.DF = {}
        self.DocTF = []
        self.DocLen = []
        self.DocIDF = {}
        self.buildDictionary()
        self.TFIDF_Generator()
        
        
    def buildDictionary(self) :
        docs = self.fn_docs
        all_tokens = sum(docs, [])
        tokens_once = [word for word in set(all_tokens) if all_tokens.count(word) == 1]
        TotWords = len(all_tokens) - len(tokens_once)
        try:
            self.DocAvgLen = TotWords/self.N
        except Exception, e:
            self.DocAvgLen = 0
            util.logger.error("Divide by zero error in Smoothness")
        self.trainCorpus = [[word for word in text if word not in tokens_once]
         for text in docs]
        self.dictionary = corpora.Dictionary(self.trainCorpus)
        
    def TFIDF_Generator(self, base=math.e) :
        trainCorpus = self.trainCorpus
        for doc in trainCorpus:
            self.DocLen.append(len(doc))
            bow = dict([(term, freq*1.0/len(doc)) for term, freq in self.dictionary.doc2bow(doc)])
            for term, tf in bow.items() :
                    if term not in self.DF :
                        self.DF[term] = 0
                    self.DF[term] += 1
            self.DocTF.append(bow)
                
        for term in self.DF:
            try:
                self.DocIDF[term] = math.log((self.N - self.DF[term] +0.5) / (self.DF[term] + 0.5), base)
            except Exception, e:
                self.DocIDF[term] = 0
                util.logger.error("Divide by zero error in smoothness")
    
    def BM25Score(self, Query=[], k1=1.5, b=0.75) :
        query_bow = self.dictionary.doc2bow(Query)
        scores = []
        for idx, doc in enumerate(self.DocTF) :
            #t0 = time()
            query_terms = dict(query_bow).keys()
            doc_terms = doc.keys()
            #t1 = time()
            #print "time 5 = "+str(t1-t0)
            if len(query_terms) < len(doc_terms):
                commonTerms = [word for word in query_terms if word  in doc_terms]
            else:
                commonTerms = [word for word in doc_terms if word  in query_terms]
           # t2 = time()
          #  print "time 6 = "+str(t2-t1)
           # commonTerms = set(dict(query_bow).keys()) & set(doc.keys())
            tmp_score = []
            doc_terms_len = self.DocLen[idx]
            for term in commonTerms :
                upper = (doc[term] * (k1+1))
                below = ((doc[term]) + k1*(1 - b + b*doc_terms_len/self.DocAvgLen))
                tmp_score.append(self.DocIDF[term] * upper / below)
            #t3 = time()
            #print "time 7 = "+str(t3-t2)
            scores.append(sum(tmp_score))
        return np.array(scores)

            