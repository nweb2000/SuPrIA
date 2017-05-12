#!/usr/bin/python
# -*- coding: utf-8 -*-

import nltk
from nltk.corpus import stopwords
from gensim import corpora, models, similarities
from gensim.models import hdpmodel, ldamodel
import operator
import util
import Constants
import os
import json

def printNormalRankedDocs(testMapping):
    result = False
    try:
        sorted_x = sorted(testMapping.items(), key=operator.itemgetter(1), reverse=True)
        todayDateFolder = util.getTodayDateFolder()
        write_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.ENGINE_DIR,
                                       todayDateFolder, Constants.GOOGLENEWS)
        if not os.path.exists(write_directory):
                os.makedirs(write_directory)
        outfile = open(os.path.join(write_directory,Constants.RELEVANCE_FILE), 'w')
        json_write = {}
        count = 1
        for (key,val) in sorted_x:
            json_write[key] = count
            count = count + 1
        json.dump(json_write, outfile)
        outfile.close()
        result = True
    except Exception, e:
        util.logger.error("Exception at printing Relevance docs for Google : %s" % write_directory)
    return result

def printSuggRankedDocs(testMapping):
    result = False
    try:
        sorted_x = sorted(testMapping.items(), key=operator.itemgetter(1), reverse=True)
        todayDateFolder = util.getTodayDateFolder()
        write_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.ENGINE_DIR,
                                       todayDateFolder, Constants.SUGG_GOOGLENEWS)
        if not os.path.exists(write_directory):
                os.makedirs(write_directory)
        outfile = open(os.path.join(write_directory,Constants.RELEVANCE_FILE), 'w')
        json_write = {}
        count = 1
        for (key,val) in sorted_x:
            json_write[key] = count
            count = count + 1
        json.dump(json_write, outfile)
        outfile.close()
        result = True
    except Exception, e:
        util.logger.error("Exception at printing Relevance docs for GoogleSugg : %s" % write_directory)
    return result


def Relevance():
    todayDate = util.getYesterdayDateFolder()
    lastRelevanceDate = util.loadSettings(Constants.LAST_RELEVANCE_DIR)
    lastSuggRelevanceDate = util.loadSettings(Constants.LAST_SUGG_RELEVANCE_DIR)
    
    if lastRelevanceDate:
        util.logger.info("Google Relevance done last for ="+lastRelevanceDate)
    else:
        util.logger.info("Google Relevance done last for None")
        
    if lastSuggRelevanceDate:
        util.logger.info("Sugg Relevance done last for ="+lastRelevanceDate)
    else:
        util.logger.info("Sugg Relevance done last for None")
        
    if todayDate == lastRelevanceDate and todayDate == lastSuggRelevanceDate:
        util.logger.info("Relevance signal already done for today :" + todayDate)
        return True
    trainFiles = util.findTrainingFiles()
    trainCorpus, usedTrainFiles = util.findCorpus(trainFiles)
    all_tokens = sum(trainCorpus, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once]
             for text in trainCorpus]        
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    tfidf = models.TfidfModel(corpus=corpus, id2word=dictionary,normalize=True)
    index = similarities.SparseMatrixSimilarity(tfidf[corpus],num_features=len(dictionary))
    
    normalRelevance = True
    if todayDate != lastRelevanceDate:
        testFiles = util.findTestFiles()
        testCorpus, usedTestFiles = util.findCorpus(testFiles)   
        count = 0
        testJson = {}
        for text in testCorpus:
            vec=dictionary.doc2bow(text)
            sims = index[tfidf[vec]]
            score = sum(sims)
            #print(list(enumerate(sims))) 
            testJson[usedTestFiles[count]] = score
            count = count + 1
        normalRelevance = printNormalRankedDocs(testJson)
        if normalRelevance == True:
            util.saveSettings(Constants.LAST_RELEVANCE_DIR, todayDate)
            util.logger.info("Google Relevance info just completed for ="+todayDate)
            
    
    suggRelevance = True
    if todayDate != lastSuggRelevanceDate:
        testFiles = util.findSuggTestFiles()
        testCorpus, usedTestFiles = util.findCorpus(testFiles)   
        count = 0
        testJson = {}
        for text in testCorpus:
            vec=dictionary.doc2bow(text)
            sims = index[tfidf[vec]]
            score = sum(sims)
            #print(list(enumerate(sims))) 
            testJson[usedTestFiles[count]] = score
            count = count + 1
        suggRelevance = printSuggRankedDocs(testJson)
        if suggRelevance == True:
            util.saveSettings(Constants.LAST_SUGG_RELEVANCE_DIR, todayDate)
            util.logger.info("Google Relevance info just completed for ="+todayDate)
    
    
    return normalRelevance or suggRelevance




            