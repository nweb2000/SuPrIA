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
import graphSeedNodes
import graphConstants
import Constants

def personalizedPageRank(R,M,S,steps=4000,tolerance=0.0000002):
      alpha= graphConstants.ALPHA_PARAM
      nodes=len(R)
      tot_sum = np.sum(R,axis = 0)
      print "old sum = "+str(tot_sum)
      R = R / tot_sum
      newR = None
      for step in range(steps):
        oldR=R
        left=alpha*np.dot(M,oldR)
        right=(1-alpha)*S
        newR=left+right
        tot_sum=0.0
        for node in range(nodes):
          tot_sum=tot_sum+abs(newR[node]-oldR[node])
        R=newR  
        #if sum<tolerance:
        #    break
        print "step =" + str(step) + " sum = " + str(tot_sum) 
        if tot_sum == 0.0:
            break
      tot_sum = np.sum(R,axis = 0)
      print "new sum = "+str(tot_sum)
      R = R / tot_sum
      return R

#Initialize R from last values
def get_init_R(G,list_nodes):
    num_nodes = len(list_nodes)
    INIT_VAL = 1.0/num_nodes
    R = np.zeros(num_nodes)
    for  node in list_nodes.keys():
        index = list_nodes[node]
        if 'weight' in G.node[node]:
            R[index] = float(G.node[node]['weight'])
        else:
            R[index] = INIT_VAL
    return R

def normalize_edge_Weights(list_nodes,G):
        # M is the transition matrix
        num_nodes = len(list_nodes)
        M = np.zeros((num_nodes,num_nodes))
        #Traverse through each node
        for node in list_nodes.keys():
            out_Edges = G.out_edges(node)
            total_edge_weight = 0.0
            for pair in out_Edges:
                out_edge_node = pair[1]
                total_edge_weight = total_edge_weight + G[node][out_edge_node]["weight"]
            
            for pair in out_Edges:
                try:
                    out_edge_node = pair[1]
                    node_idx = list_nodes[node]
                    out_edge_node_idx = list_nodes[out_edge_node]
                    if total_edge_weight != 0:
                        M[out_edge_node_idx][node_idx] = G[node][out_edge_node]["weight"]/total_edge_weight
                except Exception,e:
                    pass
            
        return M

def readLinksJson(downloadDate):
    jsonData = None
    try:
        readDirectory = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.FINAL_DIR
                                         ,downloadDate,graphConstants.ULTIMATE_FILE)
        if os.path.isfile(readDirectory) is True:
             with open(readDirectory) as json_data:
                json_text = json_data.read()
                jsonData = json.loads(json_text)
                json_data.close()
    except Exception, e:
        graphUtils.logger.error("Exception = %s" % e)
        graphUtils.logger.error("Exception at read Boiler Google recomm json for : %s" % downloadDate)
    return jsonData

def printGraphRecommendedDocs(G,list_nodes, R):
    todayDateFolder = graphUtils.getTodayDateFolder()
    jsonData = readLinksJson(todayDateFolder)
    if jsonData is None:
        return False
    
    result = False
    jsonData['GoogleNews'][Constants.NERGRAPH]=[]
    recommInfo = {}
    graphDocs = {}
    
    googleLinks = jsonData['GoogleNews'][Constants.GOOGLE]
    for linkObj in googleLinks:
        download = linkObj['download']
        htmlFile = graphConstants.TYPE_GOOGLE+"_"+linkObj['id'] + "_"+todayDateFolder
        if download == "yes" and htmlFile in list_nodes:
           recommInfo[htmlFile] = linkObj 
           htmlFile_idx =  list_nodes[htmlFile]
           graphDocs[htmlFile] = R[htmlFile_idx]
    try:
        sorted_x = sorted(graphDocs.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        write_directory = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.FINAL_DIR,todayDateFolder)
        if not os.path.exists(write_directory):
                os.makedirs(write_directory)
        outfile = open(os.path.join(write_directory,graphConstants.ULTIMATE_FILE), 'w')
        
        json_write = {}
        count = 1
        for (key,val) in sorted_x:
            if key in recommInfo:
                linkObj = recommInfo[key]
                linkObj['rank'] = -1
                jsonData['GoogleNews'][Constants.NERGRAPH].append(linkObj)
                count = count + 1
                if count >= graphConstants.RECOMMENDED_LINKS:
                    break
            else:
                graphUtils.logger.error("NER Graph normalGoogle key not found = "+key)
        json.dump(jsonData, outfile)
        outfile.close()
        result = True
    except Exception, e:
        graphUtils.logger.error("Exception = %s" % e)
        graphUtils.logger.error("Exception at writing final Graph Recommendation docs for data : %s" % write_directory)
        
        
    jsonData = readLinksJson(todayDateFolder)
    if jsonData is None:
        return False    
    jsonData['suggestGoogle'][Constants.NERGRAPH]=[]
    recommInfo = {}
    graphDocs = {}
    
    googleLinks = jsonData['suggestGoogle'][Constants.GOOGLE]
    for linkObj in googleLinks:
        download = linkObj['download']
        htmlFile = graphConstants.TYPE_SUGG+"_"+linkObj['id'] + "_"+todayDateFolder
        if download == "yes" and htmlFile in list_nodes:
           recommInfo[htmlFile] = linkObj 
           htmlFile_idx =  list_nodes[htmlFile]
           graphDocs[htmlFile] = R[htmlFile_idx]
    try:
        sorted_x = sorted(graphDocs.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        write_directory = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.FINAL_DIR,todayDateFolder)
        if not os.path.exists(write_directory):
                os.makedirs(write_directory)
        outfile = open(os.path.join(write_directory,graphConstants.ULTIMATE_FILE), 'w')
        
        json_write = {}
        count = 1
        for (key,val) in sorted_x:
            if key in recommInfo:
                linkObj = recommInfo[key]
                linkObj['rank'] = -1
                jsonData['suggestGoogle'][Constants.NERGRAPH].append(linkObj)
                count = count + 1
                if count >= graphConstants.RECOMMENDED_LINKS:
                    break
            else:
                graphUtils.logger.error("NER Graph suggestGoogle key not found = "+key)
        json.dump(jsonData, outfile)
        outfile.close()
        result = True
    except Exception, e:
        graphUtils.logger.error("Exception = %s" % e) 
        graphUtils.logger.error("Exception at writing final Graph Recommendation docs for data : %s" % write_directory)
    return result

def writeNewR(G,list_nodes, newR, graph_file):
    dict_node_weight = {}
    for node,idx in list_nodes.iteritems():
        val = newR[idx]
        if node in G.nodes():
            dict_node_weight[node] = str(val)

    nx.set_node_attributes(G, 'weight', dict_node_weight)
    nx.write_gexf(G, graph_file)

    
def PPR():
    todayDate = graphUtils.getTodayDateFolder()
    lastRecommendationnDate = graphUtils.loadSettings(graphConstants.LAST_GRAPHNER_RECOMM_DONE)
    #lastRecommendationnDate = None
    if todayDate == lastRecommendationnDate:
        graphUtils.logger.info("NER Graph recommendation done for today ")
        return
    graphUtils.logger.info("NER graph recommendation PPR last done for ="+str(lastRecommendationnDate))
     #Get the current version of stored graphs
    G = None
    graph_path = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.GRAPH_DIR, graphConstants.GRAPH_DIR, graphConstants.TYPE_NER)
    graph_file = os.path.join(graph_path,graphConstants.GRAPH_FILE)
    G = nx.read_gexf(graph_file)
    
    list_nodes = {x:i for i,x in enumerate(G.nodes())}
    R = get_init_R(G, list_nodes)
    
    #Normalize edge transition weights
    M = normalize_edge_Weights(list_nodes,G)
    
    S, list_seednode_names = graphSeedNodes.findSeedNodes(G, list_nodes)
    for idx,node in enumerate(list_seednode_names):
        graphUtils.logger.info(str(idx)+" seed node for ner graph today = "+node)
    
    newR = personalizedPageRank(R,M, S)
    printGraphRecommendedDocs(G,list_nodes, newR)
    writeNewR(G,list_nodes, newR, graph_file)
    graphUtils.saveSettings(graphConstants.LAST_GRAPHNER_RECOMM_DONE, todayDate)
    graphUtils.logger.info("ner graph recommendation done for today")
    pass
    