#!/usr/bin/python
# -*- coding: utf-8 -*-


from gensim import corpora
import operator
import graphUtils
import graphConstants
import os
import json
import math
from numpy import zeros
import numpy as np
import networkx as nx


def Smoothness():
    todayDate = graphUtils.getTodayDateFolder()
    lastSmoothnessDate = graphUtils.loadSettings(graphConstants.LAST_GRAPHNER_SMOOTHNESS_DIR)
    lastSuggSmoothnessDate = graphUtils.loadSettings(graphConstants.LAST_GRAPHNER_SUGG_SMOOTHNESS_DIR)
    
    if lastSmoothnessDate:
        graphUtils.logger.info("NERGraph Smoothness done last for ="+lastSmoothnessDate)
    else:
        graphUtils.logger.info("NERGraph Smoothness done last for None")
        
    if lastSuggSmoothnessDate:
        graphUtils.logger.info("NERGraphSugg Smoothness done last for ="+lastSuggSmoothnessDate)
    else:
        graphUtils.logger.info("NERGraphSugg Smoothness done last for None")
        
    if todayDate == lastSmoothnessDate and todayDate == lastSuggSmoothnessDate:
        graphUtils.logger.info("NERGraph Smoothness signal already done for today :" + todayDate)
        return True
    graph_path = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.GRAPH_DIR, graphConstants.GRAPH_DIR, graphConstants.TYPE_NER)
    graph_file = os.path.join(graph_path,graphConstants.GRAPH_FILE)
    write_graph_file = os.path.join(graph_path,graphConstants.GRAPH_FILE)
    if not os.path.exists(graph_path):
        os.makedirs(graph_path) 
    G = nx.read_gexf(graph_file)
    trainFiles, trainFileNames = graphUtils.findRecommTrainGraphNerFiles()
    trainCorpus = graphUtils.findCorpus(trainFiles)
    bm25obj = Bm25(trainCorpus)
    trainUniqueWords = []
    for trainText in trainCorpus:
        trainUniqueWords.append(set(trainText))     
        
    if todayDate != lastSmoothnessDate:    
        testFiles, testFileName = graphUtils.findRecommFiles()
        testCorpus = graphUtils.findCorpus(testFiles)   
        testUniqueWords = []
        mini = 100
        maxi = -1
        count = 0
        smoothness=zeros((len(testCorpus),len(trainCorpus)))
        for testText in testCorpus:
            testUniqueWords.append(set(testText))
        for testDoc in range(len(testCorpus)):
                recomm_nodename = testFileName[testDoc]
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
                dict_arr ={key: value for (key, value) in enumerate(smoothness[testDoc])}
                sorted_x = sorted(dict_arr.items(), key=operator.itemgetter(1))
                sorted_x.reverse()
                sorted_x = sorted_x[:graphConstants.MAX_SMOOTHNESS_EDGE]
                total = sum([pair[1] for pair in sorted_x])
                for (idxsim,val) in sorted_x:
                    prob = val/total
                    if recomm_nodename not in G.nodes():
                        G.add_node(recomm_nodename)
                        G.node[recomm_nodename]['type'] = graphConstants.TYPE_GOOGLE
                    trainNode = trainFileNames[idxsim]
                    if trainNode in G.nodes():
                        if prob < mini:
                            mini = prob
                        if prob > maxi:
                            maxi = prob
                        if G.has_edge(recomm_nodename,trainNode) is False:
                            G.add_edge(recomm_nodename,trainNode, weight = prob*graphConstants.SMOOTHNESS_EDGE_WEIGHT)
                        else:
                            G[recomm_nodename][trainNode]['weight'] = G[recomm_nodename][trainNode]['weight'] +  prob*graphConstants.SMOOTHNESS_EDGE_WEIGHT
                        
                        if G.has_edge(trainNode, recomm_nodename) is False:
                            G.add_edge(trainNode, recomm_nodename, weight = prob*graphConstants.SMOOTHNESS_EDGE_WEIGHT)
                        else:
                            G[trainNode][recomm_nodename]['weight'] = G[trainNode][recomm_nodename]['weight'] +  prob*graphConstants.SMOOTHNESS_EDGE_WEIGHT
                        count = count + 1 
                
                #print smoothness[testDoc]
        graphUtils.logger.info(" ner graph Smoothness completed for normalGoogle today. Stats follow")
        graphUtils.logger.info("mini =" + str(mini))
        graphUtils.logger.info( "maxi =" + str(maxi))
        graphUtils.logger.info( "Smoothness edges count ="+ str(count))
        nx.write_gexf(G, write_graph_file)
        graphUtils.saveSettings(graphConstants.LAST_GRAPHNER_SMOOTHNESS_DIR, todayDate)
        pass   
    
    if todayDate != lastSuggSmoothnessDate:    
        testFiles, testFileName = graphUtils.findSuggRecommFiles()
        testCorpus = graphUtils.findCorpus(testFiles)   
        testUniqueWords = []
        mini = 100
        maxi = -1
        count = 0
        smoothness=zeros((len(testCorpus),len(trainCorpus)))
        for testText in testCorpus:
            testUniqueWords.append(set(testText))
        for testDoc in range(len(testCorpus)):
                recomm_nodename = testFileName[testDoc]
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
                dict_arr ={key: value for (key, value) in enumerate(smoothness[testDoc])}
                sorted_x = sorted(dict_arr.items(), key=operator.itemgetter(1))
                sorted_x.reverse()
                sorted_x = sorted_x[:graphConstants.MAX_SMOOTHNESS_EDGE]
                total = sum([pair[1] for pair in sorted_x])
                for (idxsim,val) in sorted_x:
                    prob = val/total
                    if recomm_nodename not in G.nodes():
                        G.add_node(recomm_nodename)
                        G.node[recomm_nodename]['type'] = graphConstants.TYPE_SUGG
                    trainNode = trainFileNames[idxsim]
                    if trainNode in G.nodes():
                        if prob < mini:
                            mini = prob
                        if prob > maxi:
                            maxi = prob
                        if G.has_edge(recomm_nodename,trainNode) is False:
                            G.add_edge(recomm_nodename,trainNode, weight = prob*graphConstants.SMOOTHNESS_EDGE_WEIGHT)
                        else:
                            G[recomm_nodename][trainNode]['weight'] = G[recomm_nodename][trainNode]['weight'] +  prob*graphConstants.SMOOTHNESS_EDGE_WEIGHT
                        
                        if G.has_edge(trainNode, recomm_nodename) is False:
                            G.add_edge(trainNode, recomm_nodename, weight = prob*graphConstants.SMOOTHNESS_EDGE_WEIGHT)
                        else:
                            G[trainNode][recomm_nodename]['weight'] = G[trainNode][recomm_nodename]['weight'] +  prob*graphConstants.SMOOTHNESS_EDGE_WEIGHT
                        count = count + 1 
                
                #print smoothness[testDoc]
        graphUtils.logger.info(" ner graph Smoothness completed for suggestGoogle today. Stats follow")
        graphUtils.logger.info("mini =" + str(mini))
        graphUtils.logger.info( "maxi =" + str(maxi))
        graphUtils.logger.info( "Smoothness edges count ="+ str(count))
        nx.write_gexf(G, write_graph_file)
        graphUtils.saveSettings(graphConstants.LAST_GRAPHNER_SUGG_SMOOTHNESS_DIR, todayDate)
        pass   

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
        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        TotWords = len(all_tokens) - len(tokens_once)
        try:
            self.DocAvgLen = TotWords/self.N
        except Exception, e:
            self.DocAvgLen = 0
            graphUtils.logger.error("Divide by zero error in Smoothness")
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
                graphUtils.logger.error("Divide by zero error in smoothness")
    
    def BM25Score(self, Query=[], k1=1.5, b=0.75) :
        query_bow = self.dictionary.doc2bow(Query)
        scores = []
        for idx, doc in enumerate(self.DocTF) :
            commonTerms = set(dict(query_bow).keys()) & set(doc.keys())
            tmp_score = []
            doc_terms_len = self.DocLen[idx]
            for term in commonTerms :
                upper = (doc[term] * (k1+1))
                below = ((doc[term]) + k1*(1 - b + b*doc_terms_len/self.DocAvgLen))
                tmp_score.append(self.DocIDF[term] * upper / below)
            scores.append(sum(tmp_score))
        return np.array(scores)

            