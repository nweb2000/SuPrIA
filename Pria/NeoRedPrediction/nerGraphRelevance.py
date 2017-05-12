#!/usr/bin/python
# -*- coding: utf-8 -*-

import nltk
from nltk.corpus import stopwords
from gensim import corpora, models, similarities
from gensim.models import hdpmodel, ldamodel
import operator
import graphUtils
import graphConstants
import os
import json
import networkx as nx
import string
import re
from nltk.tag.stanford import StanfordNERTagger
from itertools import groupby

def Relevance():
    todayDate = graphUtils.getTodayDateFolder()
    lastRelevanceDate = graphUtils.loadSettings(graphConstants.LAST_GRAPHNER_RELEVANCE_DIR)
    lastSuggRelevanceDate = graphUtils.loadSettings(graphConstants.LAST_GRAPHNER_SUGG_RELEVANCE_DIR)
    
    if lastRelevanceDate:
        graphUtils.logger.info("nerGraph Relevance done last for ="+lastRelevanceDate)
    else:
        graphUtils.logger.info("nerGraph Relevance done last for None")
        
    if lastSuggRelevanceDate:
        graphUtils.logger.info("nerGraphSugg Relevance done last for ="+lastSuggRelevanceDate)
    else:
        graphUtils.logger.info("nerGraphSugg Relevance done last for None")
        
    if todayDate == lastRelevanceDate and todayDate == lastSuggRelevanceDate:
        graphUtils.logger.info("nerGraph Relevance signal already done for today :" + todayDate)
        return True
    graph_path = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.GRAPH_DIR, graphConstants.GRAPH_DIR, graphConstants.TYPE_NER)
    graph_file = os.path.join(graph_path,graphConstants.GRAPH_FILE)
    write_graph_file = os.path.join(graph_path,graphConstants.GRAPH_FILE)
    if not os.path.exists(graph_path):
        os.makedirs(graph_path) 
    G = nx.read_gexf(graph_file)
    trainFiles, trainFileNames = graphUtils.findRecommTrainGraphNerFiles()
    trainCorpus = graphUtils.findCorpus(trainFiles)
    all_tokens = sum(trainCorpus, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once]
             for text in trainCorpus]        
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    tfidf = models.TfidfModel(corpus=corpus, id2word=dictionary,normalize=True)
    index = similarities.SparseMatrixSimilarity(tfidf[corpus],num_features=len(dictionary))
    
    
    if todayDate != lastRelevanceDate:
        testFiles, testFileName = graphUtils.findRecommFiles()
        testCorpus = graphUtils.findCorpus(testFiles)   
        mini = 100
        maxi = -1
        count = 0
        for idx,text in enumerate(testCorpus):
                #Add this recommendation node
                recomm_nodename = testFileName[idx]
                if recomm_nodename not in G.nodes():
                    G.add_node(recomm_nodename)
                    G.node[recomm_nodename]['type'] = graphConstants.TYPE_GOOGLE
                vec=dictionary.doc2bow(text)
                sims = index[tfidf[vec]]
                for idxsim,prob in enumerate(sims):
                    if prob < 0.1:
                        continue
                    trainNode = trainFileNames[idxsim]
                    if trainNode in G.nodes():
                        if prob < mini:
                            mini = prob
                        if prob > maxi:
                            maxi = prob
                        G.add_edge(recomm_nodename,trainNode, weight = prob)
                        G.add_edge(trainNode,recomm_nodename, weight = prob)
                        count = count + 1
                text = readFromFile(testFiles[idx])
                NERFunc(text,G, recomm_nodename)
        graphUtils.logger.info("Ner graph relevance completed for normalGoogle today. Stats follow")
        graphUtils.logger.info("mini =" + str(mini))
        graphUtils.logger.info( "maxi =" + str(maxi))
        graphUtils.logger.info( "Relevance count ="+ str(count))
        graphUtils.saveSettings(graphConstants.LAST_GRAPHNER_RELEVANCE_DIR, todayDate)
        
        
    if todayDate != lastRelevanceDate:
        testFiles, testFileName = graphUtils.findSuggRecommFiles()
        testCorpus = graphUtils.findCorpus(testFiles)   
        mini = 100
        maxi = -1
        count = 0
        for idx,text in enumerate(testCorpus):
                #Add this recommendation node
                recomm_nodename = testFileName[idx]
                if recomm_nodename not in G.nodes():
                    G.add_node(recomm_nodename)
                    G.node[recomm_nodename]['type'] = graphConstants.TYPE_SUGG
                vec=dictionary.doc2bow(text)
                sims = index[tfidf[vec]]
                for idxsim,prob in enumerate(sims):
                    if prob < 0.1:
                        continue
                    trainNode = trainFileNames[idxsim]
                    if trainNode in G.nodes():
                        if prob < mini:
                            mini = prob
                        if prob > maxi:
                            maxi = prob
                        G.add_edge(recomm_nodename,trainNode, weight = prob)
                        G.add_edge(trainNode,recomm_nodename, weight = prob)
                        count = count + 1
                text = readFromFile(testFiles[idx])
                NERFunc(text,G, recomm_nodename)
        graphUtils.logger.info("Ner graph relevance completed for suggestGoogle today. Stats follow")
        graphUtils.logger.info("mini =" + str(mini))
        graphUtils.logger.info( "maxi =" + str(maxi))
        graphUtils.logger.info( "Relevance count ="+ str(count))
        nx.write_gexf(G, write_graph_file)
        graphUtils.saveSettings(graphConstants.LAST_GRAPHNER_SUGG_RELEVANCE_DIR, todayDate)
    pass

def readFromFile(filepath):
    data = None
    try:
        f = open(filepath,"r")
        data = f.read()
        f.close()   
    except Exception, e:
            print "Exception at writing file: %s" % e
    return data

def NERFunc(data,G, node_name):
    os.environ["STANFORD_MODELS"] = os.path.join(graphConstants.ROOT_FOLDER,"stanford-ner-2015-04-20")
    st = StanfordNERTagger(os.path.join(graphConstants.ROOT_FOLDER,"stanford-ner-2015-04-20","classifiers","english.all.3class.distsim.crf.ser.gz"),
                          os.path.join(graphConstants.ROOT_FOLDER,"stanford-ner-2015-04-20","stanford-ner.jar" ))
    if data is not None:
           
                netagged_words = st.tag(data.split())
                for tag, chunk in groupby(netagged_words, lambda x:x[1]):
                    if tag != "O":
                        entity = " ".join(w for w, t in chunk)
                        if  entity != "":
                            entity = entity.encode('utf-8')
                            entity = re.sub(r'[^\x00-\x7F]+', ' ', entity)
                            entity = entity.lower()
                            no_punctuation = entity.translate(None, string.punctuation)
                            entity=re.sub("[^a-zA-Z]+", " ", no_punctuation)
                            #print("Tag = "+ tag+" entity = "+ entity)
                            #If this topic doesn't exist as a node then add it
                            if entity not in G.nodes():
                                continue
                            #If the edge between this doc and entity is already present or not
                            if G.has_edge(node_name,entity) is False:
                                G.add_edge(node_name,entity, weight = 1)
                            else:
                                G[node_name][entity]["weight"] = G[node_name][entity]["weight"] + 1
                                graphUtils.logger.info("Recomm entity NER topic entity = "+entity + " document ="+node_name)
                            if G.has_edge(entity,node_name) is False:
                                G.add_edge(entity,node_name, weight = 1)
                            else:
                                G[entity][node_name]["weight"] = G[entity][node_name]["weight"] + 1
                            
                            topics = entity.split()
                            if(len(topics) > 1):
                                for word in entity.split():
                                    #Only change weight if this topic already exists
                                    if word in G.nodes():
                                        #If the edge between this doc and topic is already present or not
                                        if G.has_edge(node_name,word) is False:
                                            G.add_edge(node_name,word, weight = 1)
                                        else:
                                            G[node_name][word]["weight"] = G[node_name][word]["weight"] + 1
                                        if G.has_edge(word,node_name) is False:
                                            G.add_edge(word,node_name, weight = 1)
                                        else:
                                            G[word][node_name]["weight"] = G[word][node_name]["weight"] + 1
                                        graphUtils.logger.info("Recomm entity NER topic word = "+word + " document ="+node_name)
   