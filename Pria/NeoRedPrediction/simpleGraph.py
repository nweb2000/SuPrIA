import graphConstants
import graphUtils
import nltk
import string
from bs4 import BeautifulSoup
import traceback
from os import listdir
from os.path import isfile, join
import os
import re
from nltk.corpus import stopwords
from numpy import zeros
from gensim import corpora, models, similarities
from gensim.models import hdpmodel, ldamodel
from math import log
import numpy as np
import operator
import networkx as nx
import graphNER
LDA_PASSES = 20
from time import time
class MyCorpus(corpora.TextCorpus):
    def get_texts(self):
        if not hasattr(self, 'corpus'):
            self.corpus = [text for text in self.input]
        for filedata in self.input:
            yield filedata
    def update_dictionary(self,new_texts):
        self.dictionary.add_documents(new_texts, prune_at=graphConstants.DICTIONARY_MAXLEN)
    def update_corpus(self, new_texts):
        self.corpus.extend(new_texts)
        self.update_dictionary(new_texts)
    def get_corpus(self):
        return self.corpus

def buildGraph():
    #Load up the current graph we may have
    
    
    #Last Graph date done
    date_LAST_GRAPH_DONE = graphUtils.loadSettings(graphConstants.date_LAST_GRAPH_DONE)
    date_LAST_TEXTCORPUS_DONE = graphUtils.loadSettings(graphConstants.date_LAST_TEXTCORPUS_DONE)
    date_LAST_LDA_DONE = graphUtils.loadSettings(graphConstants.date_LAST_LDA_DONE)
    yesterdayFolder = graphUtils.getYesterdayDateFolder()
    if date_LAST_GRAPH_DONE == yesterdayFolder:
        graphUtils.logger.info("simple Graph already built till yesterday")
        return
    graphFiles, graphFileNames = graphUtils.findGraphFiles()
    graphCorpus = graphUtils.findCorpus(graphFiles)
    all_tokens = sum(graphCorpus, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    new_texts = [[word for word in text if word not in tokens_once]
         for text in graphCorpus]
    pass
    
    #Retrieve text corpus
    txtcorpus_path = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.GRAPH_DIR, graphConstants.TEXTCORPUS_DIR, graphConstants.TYPE_MAIN)
    txtcorpus_file = os.path.join(txtcorpus_path,graphConstants.TEXTCORPUS_FILE)
    if not os.path.exists(txtcorpus_path):
        os.makedirs(txtcorpus_path)
    objtxt_corpus = None
    if date_LAST_TEXTCORPUS_DONE == None:
        objtxt_corpus = MyCorpus(new_texts)
        objtxt_corpus.save(txtcorpus_file)
        graphUtils.saveSettings(graphConstants.date_LAST_TEXTCORPUS_DONE, yesterdayFolder)
    elif date_LAST_TEXTCORPUS_DONE != yesterdayFolder:
        objtxt_corpus = MyCorpus.load(txtcorpus_file)
        objtxt_corpus.update_corpus(new_texts)
        objtxt_corpus.save(txtcorpus_file)
        graphUtils.saveSettings(graphConstants.date_LAST_TEXTCORPUS_DONE, yesterdayFolder)
    else:
        objtxt_corpus = MyCorpus.load(txtcorpus_file)
    
    txt_dictionary = objtxt_corpus.dictionary
    corpus = [txt_dictionary.doc2bow(text) for text in objtxt_corpus.corpus]
    newtxt_corpus = [txt_dictionary.doc2bow(text) for text in new_texts]
    
    tfidf = models.TfidfModel(corpus=corpus, id2word=txt_dictionary,normalize=True)
    idf = models.tfidfmodel.precompute_idfs(tfidf.wglobal,txt_dictionary.dfs,len(corpus))
    
    if date_LAST_LDA_DONE!= None:
        graphUtils.logger.info("Simple graph nodes lda after ="+date_LAST_LDA_DONE+" starts")
    else:
        graphUtils.logger.info("Simple graph nodes lda after = none starts")
    t0 = time()
    #Do lda
    #Retrieve text corpus
    lda_path = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.GRAPH_DIR, graphConstants.LDA_DIR, graphConstants.TYPE_MAIN)
    lda_file = os.path.join(lda_path,graphConstants.LDA_FILE)
    lda = None
    if not os.path.exists(lda_path):
        os.makedirs(lda_path)
    date_LAST_LDA_DONE = None
    if date_LAST_LDA_DONE == None:
        lda = models.LdaModel(corpus=corpus, id2word=txt_dictionary, num_topics=50, \
                               update_every=1, chunksize=10000, passes=LDA_PASSES)
        lda.save(lda_file)
        graphUtils.saveSettings(graphConstants.date_LAST_LDA_DONE, yesterdayFolder)
    elif date_LAST_LDA_DONE != yesterdayFolder:
        lda = models.LdaModel.load(lda_file)
        lda.update(newtxt_corpus)
        lda.save(lda_file)
        graphUtils.saveSettings(graphConstants.date_LAST_LDA_DONE, yesterdayFolder)
    else:
        lda = models.LdaModel.load(lda_file)
    
    t1= time()
    graphUtils.logger.info("Simple graph nodes lda time ="+str(t1-t0)+" seconds ends")
    #Develop graph
    G = None
    graph_path = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.GRAPH_DIR, graphConstants.GRAPH_DIR, graphConstants.TYPE_MAIN)
    graph_file = os.path.join(graph_path,graphConstants.GRAPH_FILE)
    if not os.path.exists(graph_path):
        os.makedirs(graph_path)
    if date_LAST_GRAPH_DONE == None:
        G=nx.DiGraph()    
    elif date_LAST_GRAPH_DONE != yesterdayFolder:
        G = nx.read_gexf(graph_file)
    
    if date_LAST_GRAPH_DONE != None:
        graphUtils.logger.info("Simple graph nodes addition after ="+date_LAST_GRAPH_DONE+" starts")
    else:
        graphUtils.logger.info("Simple graph nodes addition after = None")
    #Add nodes and edges for current new corpus which is supposed to be added    
    if date_LAST_GRAPH_DONE != yesterdayFolder:
        for topic in [50]:
            for index,document in enumerate(newtxt_corpus):
                node_name = graphFileNames[index]
                G.add_node(node_name)
                G.node[node_name]['type'] = graphConstants.TYPE_HISTORY
                topics = lda[document]
                #print "Document start"
                for topicObj,topicProb in topics:
                    #Compare topicProb with some threshold value
                    if topicProb > 0.1:
                        topicid = topicObj
                        words = lda.show_topic(topicid, topn=10)
                        for wordProb, word in words:
                            wordId = txt_dictionary.doc2bow([word])[0][0]
                            idfWord = idf[wordId]
                            if idfWord > 3.0:
                                word = word.lower()
                                #If this topic doesn't exist as a node then add it
                                if word not in G.nodes():
                                    G.add_node(word)
                                    G.node[word]['type'] = graphConstants.TYPE_TOPICS
                                #If the edge between this doc and topic is already present or not
                                if G.has_edge(node_name,word) is False:
                                    G.add_edge(node_name,word, weight = 1)
                                else:
                                    G[node_name][word]["weight"] = G[node_name][word]["weight"] + 1
                                if G.has_edge(word,node_name) is False:
                                    G.add_edge(word,node_name, weight = 1)
                                else:
                                    G[word][node_name]["weight"] = G[word][node_name]["weight"] + 1
                               # print "word = "+word + " document ="+node_name
                                graphUtils.logger.info("word = "+word + " document ="+node_name)
                                #print "Word = "+word + " idf="+str(idfWord)
                            pass
                        
                        
            #f=open('lda_topics_'+str(topic)+'_'+str(LDA_PASSES)+'_'+'.txt','w')
            # Prints the topics.
            #for top in lda.print_topics(num_words=1000,num_topics=topic):
            #    f.write(top+' \n')
            #print 'Document topic printed for'+str(topic)
        #G = NER.NERFunc(graphFiles, graphFileNames, G)
        nx.write_gexf(G, graph_file)
        graphUtils.saveSettings(graphConstants.date_LAST_GRAPH_DONE, yesterdayFolder)
        graphUtils.logger.info("Simple graph nodes addition after ="+str(date_LAST_GRAPH_DONE)+" ends")
        