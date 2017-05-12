#!/usr/bin/python
# -*- coding: utf-8 -*-


from gensim import corpora
from gensim import corpora, models, similarities
from gensim.models import hdpmodel, ldamodel
import operator
import graphUtils
import graphConstants
import os
import json
import math
from numpy import zeros
import numpy as np
from time import time
import networkx as nx

def ConnectionClarity():
    todayDate = graphUtils.getYesterdayDateFolder()
    lastClarityDate = graphUtils.loadSettings(graphConstants.LAST_GRAPH_CLARITY_DIR)
    lastSuggClarityDate = graphUtils.loadSettings(graphConstants.LAST_GRAPH_SUGG_CLARITY_DIR)
    if lastClarityDate:
        graphUtils.logger.info("Graph Google Clarity done last for ="+lastClarityDate)
    else:
        graphUtils.logger.info("Graph Google Clarity done last for none")
        
    if lastSuggClarityDate:
        graphUtils.logger.info("Graph Sugg Clarity done last for ="+lastSuggClarityDate)
    else:
        graphUtils.logger.info("Graph Sugg Clarity done last for none")
        
    if todayDate == lastClarityDate and todayDate == lastSuggClarityDate:
        graphUtils.logger.info("graph Clarity signal done for today =" + todayDate)
        return True
    
    graph_path = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.GRAPH_DIR, graphConstants.GRAPH_DIR, graphConstants.TYPE_MAIN)
    graph_file = os.path.join(graph_path,graphConstants.GRAPH_FILE)
    write_graph_file = os.path.join(graph_path,graphConstants.GRAPH_FILE)
    if not os.path.exists(graph_path):
        os.makedirs(graph_path) 
    G = nx.read_gexf(graph_file)
    trainFiles, trainFileNames = graphUtils.findRecommTrainGraphFiles()
    
    
    trainCorpus = graphUtils.findCorpus(trainFiles)
    if todayDate != lastClarityDate:
        testFiles, testFileName =graphUtils.findRecommFiles()
        testCorpus = graphUtils.findCorpus(testFiles)   
        clarityobj = Clarity(trainCorpus,testCorpus)
        clarityScore = clarityobj.ClarityScore()
        mini = 100
        maxi = -1
        count = 0
        for testidx,text in enumerate(testCorpus):
            recomm_nodename = testFileName[testidx]
            dict_arr ={key: value for (key, value) in enumerate(clarityScore[testidx])}
            sorted_x = sorted(dict_arr.items(), key=operator.itemgetter(1))
            sorted_x.reverse()
            sorted_x = sorted_x[:graphConstants.MAX_CLARITY_EDGE]
            total = sum([pair[1] for pair in sorted_x])
            for (idxsim,val) in sorted_x:
                    prob = val/total
                    if prob < 0.0:
                        break
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
                            G.add_edge(recomm_nodename,trainNode, weight = prob*graphConstants.CLARITY_EDGE_WEIGHT)
                        else:
                            G[recomm_nodename][trainNode]['weight'] = G[recomm_nodename][trainNode]['weight'] +  prob*graphConstants.CLARITY_EDGE_WEIGHT
                        
                        if G.has_edge(trainNode, recomm_nodename) is False:
                            G.add_edge(trainNode, recomm_nodename, weight = prob*graphConstants.CLARITY_EDGE_WEIGHT)
                        else:
                            G[trainNode][recomm_nodename]['weight'] = G[trainNode][recomm_nodename]['weight'] +  prob*graphConstants.CLARITY_EDGE_WEIGHT
                            
                        count = count + 1 
        
        graphUtils.logger.info("Simple  graph clarity completed for googlenews today. Stats follow")
        graphUtils.logger.info("mini =" + str(mini))
        graphUtils.logger.info( "maxi =" + str(maxi))
        graphUtils.logger.info( "clarity edges count ="+ str(count))
        nx.write_gexf(G, write_graph_file)
        graphUtils.saveSettings(graphConstants.LAST_GRAPH_CLARITY_DIR, todayDate)
        pass 
    
    if todayDate != lastSuggClarityDate:
        testFiles, testFileName =graphUtils.findSuggRecommFiles()
        testCorpus = graphUtils.findCorpus(testFiles)   
        clarityobj = Clarity(trainCorpus,testCorpus)
        clarityScore = clarityobj.ClarityScore()
        mini = 100
        maxi = -1
        count = 0
        for testidx,text in enumerate(testCorpus):
            recomm_nodename = testFileName[testidx]
            dict_arr ={key: value for (key, value) in enumerate(clarityScore[testidx])}
            sorted_x = sorted(dict_arr.items(), key=operator.itemgetter(1))
            sorted_x.reverse()
            sorted_x = sorted_x[:graphConstants.MAX_CLARITY_EDGE]
            total = sum([pair[1] for pair in sorted_x])
            for (idxsim,val) in sorted_x:
                    prob = val/total
                    if prob < 0.0:
                        break
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
                            G.add_edge(recomm_nodename,trainNode, weight = prob*graphConstants.CLARITY_EDGE_WEIGHT)
                        else:
                            G[recomm_nodename][trainNode]['weight'] = G[recomm_nodename][trainNode]['weight'] +  prob*graphConstants.CLARITY_EDGE_WEIGHT
                        
                        if G.has_edge(trainNode, recomm_nodename) is False:
                            G.add_edge(trainNode, recomm_nodename, weight = prob*graphConstants.CLARITY_EDGE_WEIGHT)
                        else:
                            G[trainNode][recomm_nodename]['weight'] = G[trainNode][recomm_nodename]['weight'] +  prob*graphConstants.CLARITY_EDGE_WEIGHT
                            
                        count = count + 1 
        
        graphUtils.logger.info("Simple  graph clarity completed for SuggestGoogle today. Stats follow")
        graphUtils.logger.info("mini =" + str(mini))
        graphUtils.logger.info( "maxi =" + str(maxi))
        graphUtils.logger.info( "clarity edges count ="+ str(count))
        nx.write_gexf(G, write_graph_file)
        graphUtils.saveSettings(graphConstants.LAST_GRAPH_SUGG_CLARITY_DIR, todayDate)
        pass 
class Clarity:
    
    def __init__(self, fn_docs, test_docs) :
        self.NUM_RELEVANT = 5
        self.fn_docs = fn_docs
        self.test_docs = test_docs
        self.N = 0
        self.DocAvgLen = 0
        self.wGivenR = []
        self.DF = {}
        self.DocTF = []
        self.DocLen = []
        self.DocIDF = {}
        self.buildDictionary()
        self.TFIDF_Generator()
        self.init_tfidf()
        
    def buildDictionary(self) :
        docs = self.fn_docs
        all_tokens = sum(docs, [])
        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        TotWords = len(all_tokens) - len(tokens_once)
        self.trainCorpus = [[word for word in text if word not in tokens_once]
         for text in docs]
        self.trainCorpus = [x for x in self.trainCorpus if x != []]
        self.N = len(self.trainCorpus)
        self.dictionary = corpora.Dictionary(self.trainCorpus)
        try:
            self.DocAvgLen = TotWords/self.N
        except Exception, e:
            self.DocAvgLen = 0
            graphUtils.logger.error("Divide by zero error in clarity")
        if self.N < self.NUM_RELEVANT:
            self.NUM_RELEVANT = self.N
        self.TotWords = TotWords
        
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
        try:
            wGivenC = [float(self.DF[term])/self.TotWords for term in range(len(self.dictionary.keys()))]    
            self.wGivenC = np.asarray(wGivenC)
        except Exception, e:
            self.wGivenC = 0
            graphUtils.logger.error("Divide by zero error in clarity")
        
        
    def init_tfidf(self):
         corpus = [self.dictionary.doc2bow(text) for text in self.trainCorpus]
         self.tfidf = models.TfidfModel(corpus=corpus, id2word=self.dictionary,normalize=True)
         self.index = similarities.SparseMatrixSimilarity(self.tfidf[corpus],num_features=len(self.dictionary))
         
    def findMostRelevant(self,vec):
         sims = self.index[self.tfidf[vec]]
         sorted_index = [i[0] for i in sorted(enumerate(sims), key=lambda x:x[1], reverse = True)]
         return sorted_index[:self.NUM_RELEVANT]
    
    def computeWgivenRdash(self,trainIdx, testQuery, listRelevant):
        wGivenRdash = np.ones(self.NUM_RELEVANT)
        
        trainQuery = self.trainCorpus[trainIdx]
        testDoc = dict(testQuery)
        trainDoc = dict(self.dictionary.doc2bow(trainQuery))
        commonTerms = set(testDoc.keys()) & set(trainDoc.keys())
        
        
        for term in commonTerms :
            trainWordLen = trainDoc[term]
            testWordLen = testDoc[term]
            power = trainWordLen if trainWordLen < testWordLen else testWordLen
            wGivenRdash = wGivenRdash * np.asarray([math.pow(doc[term], power) if term in doc else 1    for doc in listRelevant])
        return wGivenRdash
                
                
                    
    def ClarityScore(self) :     
        finalScore=zeros((len(self.test_docs),self.N))
        for tstIndex, testText in enumerate(self.test_docs):
            testQuery = self.dictionary.doc2bow(testText)
            relevantSet = self.findMostRelevant(testQuery)
            listRelevant = []
            tokens = self.dictionary.keys()
            for i in range(self.NUM_RELEVANT):
                relevantQuery = self.DocTF[relevantSet[i]]
                listRelevant.append(relevantQuery)
            for idx, trainDoc in enumerate(self.DocTF):
                try:
                    t0 = time()
                    wGivenRdash = self.computeWgivenRdash(idx, testQuery, listRelevant)
                    wGivenR = [ [ doc[term] if term in doc else 0 for term in range(len(self.dictionary.keys()))]  for doc in listRelevant]
                    wGivenR = np.asarray(wGivenR)
                    wGivenSD = [wGivenR[x]*wGivenRdash[x] for x in range(self.NUM_RELEVANT) ]
                    wGivenSD = np.asarray(wGivenSD)
                    finalWSD = wGivenSD[0] + wGivenSD[1] + wGivenSD[2] + wGivenSD[3] + wGivenSD[4] 
                    temp1 = finalWSD/self.wGivenC
                    temp2 = np.where(temp1>0, np.log(temp1), 0)
                    #temp2 = np.log(temp1)
                    prod = temp2 * finalWSD
                    finalScore[tstIndex][idx] = np.sum(prod)
                    t1 = time()
                    #print "for %d and %d it took %d seconds score = %f" % (tstIndex, idx, t1-t0, finalScore[tstIndex][idx])
                    pass
                except Exception, e:
                    finalScore[tstIndex][idx] = 0
                    graphUtils.logger.error("Divide by zero error in clarity")
        return finalScore
                
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

            