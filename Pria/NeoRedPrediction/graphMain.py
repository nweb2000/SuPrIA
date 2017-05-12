

import traceback
import simpleGraph
import graphUtils
import simpleGraphRecommendation
import graphNER
import nerGraphRecommendation
def graphStart():
    try:
        graphUtils.initLogger()
        graphUtils.initGlobal()
        graphUtils.initSettings()
        graphUtils.logger.info("Start simple graph for today")
        simpleGraph.buildGraph()
        simpleGraphRecommendation.Recommendation()
        graphUtils.logger.info("Start ner graph for today")
        graphNER.buildGraph()
        nerGraphRecommendation.Recommendation()
    except Exception, e:
        print "Exception at NeoRedPrediction : %s" % traceback.print_exc()
    



            