import operator
import graphConstants
import numpy as np
import networkx as nx




def findSeedNodes(G, list_nodes):
    #forced_nodes = ["paris","attacks","rollins","ambrose","reigns","sachin"]
    list_seednode_names = []
    forced_nodes = []
    S = np.zeros(len(G.nodes()))
    dict_nodes = {}
    #Find the top 5 topics
    for node in G.nodes():
        try:
            if G.node[node]['type'] == graphConstants.TYPE_TOPICS or G.node[node]['type'] == graphConstants.TYPE_NER:
                out_Edges = G.out_edges(node)
                num_Edges = len(out_Edges)
                if num_Edges > graphConstants.THRESHOLD_SEED_EDGE:
                    print node
                    dict_nodes[node] = num_Edges
        except Exception, e:
            print "exception"
    sorted_x = sorted(dict_nodes.items(), key=operator.itemgetter(1))
    sorted_x.reverse()
    for item in sorted_x:
        print item
    topSeedNodes = sorted_x[:graphConstants.NUM_SEED_NODES]
    for seedNode, outEdge in topSeedNodes:
        seedNode_idx = list_nodes[seedNode]
        S[seedNode_idx] = 1.0
        list_seednode_names.append(seedNode)
        
    for seedNode in forced_nodes:
        seedNode_idx = list_nodes[seedNode]
        S[seedNode_idx] = 1.0
    return S, list_seednode_names