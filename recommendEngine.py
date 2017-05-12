############################
# Main recommendation engine
############################# 
import corpus_utils
import feedparse as fp
import RssParser
from gensim import models
from scipy import spatial
import math
import numpy as np

def get_scores(user_data_file, rss_feed, vectmodel, ldamodel, alpha = 0.5):
    user_text = corpus_utils.SingleUserTwitterGen(user_data_file).get_tweets()
    user_vec = vectmodel.infer_vector(user_text, steps=10)
#    print(user_vec)
    rss_vects = [vectmodel.infer_vector((x.title + " " + x.descrip).split(), steps=10) for x in rss_feed]
    sims = compute_sims(user_vec, rss_vects, vectmodel)
    print("Sims")
    print(sims)
    posts = [compute_posterior(x, ldamodel) for x in rss_feed]
    print("Posts")
    print(posts)
#    scores = (1-alpha)*np.array(sims) + (alpha)*np.array(posts)
    scores = np.array(sims) + (alpha)*np.array(posts)
    print("Scores")
    print(scores)

    print("Computed Scores")
    return list(enumerate(scores))


def compute_sims(user_vect, rss_vects, model):
    sims = [1-spatial.distance.cosine(user_vect, v) for v in rss_vects]
    return sims

def compute_posterior(rss_item, ldamodel):
    post = 0
    vocab = list(ldamodel.id2word.values())
    rss_str = (rss_item.title + " " + rss_item.descrip).split()
    rss_str = [x for x in rss_str if x in vocab]
#    print(rss_str)
    for t in range(ldamodel.num_topics):
        dist = dict(ldamodel.show_topic(t, len(ldamodel.id2word)))
        for w in rss_str:
            post += math.log(dist[w])
    return post
             
def get_queries(k, user_data_file, rss_feed, vectmodel, ldamodel, alpha = 0.5):
    """
    Get k queries
    """
    scores = get_scores(user_data_file, rss_feed, vectmodel, ldamodel, alpha)
    sorted_score = sorted(scores,key= lambda x: x[1], reverse=True)
    indices = [x[0] for x in sorted_score[:k]]
    queries = [rss_feed[x] for x in indices]
    return queries

if __name__ == "__main__":
    ldamodel=models.ldamodel.LdaModel.load("models/ldamodel_2")
    vectmodel = models.Doc2Vec.load("models/twitterModelTrimmed.model")
    print("Loaded Models")
    dudebrochill = "data/dudebrochill"
    artistrickards = "data/artistrickards"
    laytechs = "data/laytechs"
    lovetoedit = "data/lovetoeditfilm"
    web20builders = "data/web20builders"
    sportsgratr= "data/sportsgratr"

    rss_feed = RssParser.all_cat()       
    

    queries1 =get_queries(15, dudebrochill, rss_feed, vectmodel, ldamodel)
    print("1")
    queries2 =get_queries(15, artistrickards, rss_feed, vectmodel, ldamodel)
    print("2")
    queries3 =get_queries(15, laytechs, rss_feed, vectmodel, ldamodel, alpha=0.00005)
    print("3")
    queries4 =get_queries(15,lovetoedit, rss_feed, vectmodel, ldamodel, alpha=0.00005)
    print("4")
    queries5 =get_queries(15, web20builders, rss_feed, vectmodel, ldamodel)
    print("5")
    queries6 =get_queries(15,sportsgratr, rss_feed, vectmodel, ldamodel, alpha=0.00005)
    print("6")

    with open("outfile", 'w') as outfile:
#        print([x.title for x in queries1])
#        outfile.write("\n".join([x.title for x in queries1]))
#        outfile.write("-------------------")
#        print("-------")
#        print([x.title for x in queries2])
#        outfile.write("\n".join([x.title for x in queries2]))
#        outfile.write("-------------------")

#        print("-------")
        print([x.title for x in queries3])
        outfile.write("\n".join([x.title for x in queries3]))
        outfile.write("-------------------")

        print("-------")
        print([x.title for x in queries4])
        outfile.write("\n".join([x.title for x in queries4]))
        outfile.write("-------------------")

#        print("-------")
#        print([x.title for x in queries5])
#        outfile.write("\n".join([x.title for x in queries5]))
#        outfile.write("-------------------")

        print("-------")
        print([x.title for x in queries6])
        outfile.write("\n".join([x.title for x in queries6]))
        outfile.write("-------------------")

        
        


