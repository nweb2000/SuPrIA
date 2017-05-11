############################
# Main recommendation engine
############################# 
import corpus_utils
import feedparse as fp
from gensim import models
from scipy import spatial
import math
import numpy as np

def get_scores(user_data_file, rss_feed, vectmodel, ldamodel, alpha = 0.5):
    user_text = corpus_utils.SingleUserTwitterGen(user_data_file).get_tweets()
    user_vec = vectmodel.infer_vector(user_text, steps=10)
    rss_vects = [vectmodel.infer_vector((x.title + " " + x.descrip).split()) for x in rss_feed]
    sims = compute_sims(user_vec, rss_vects, vectmodel)
    posts = [compute_posterior(x, ldamodel) for x in rss_feed]
    scores = (1-alpha)*np.array(sims) + (alpha)*np.array(posts)
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
    print(rss_str)
    for t in range(ldamodel.num_topics):
        dist = dict(ldamodel.show_topic(t, len(ldamodel.id2word)))
        for w in rss_str:
            post += math.log(dist[w])
    return post
             
def get_queries(k, user_data_file, rss_url, vectmodel, ldamodel, alpha = 0.5):
    """
    Get k queries
    """
    rss_feed = fp.getRssFeed(rss_url)
    scores = get_scores(user_data_file, rss_feed, vectmodel, ldamodel, alpha)
    sorted_score = sorted(scores,key= lambda x: x[1])
    indices = [x[0] for x in sorted_score[:k]]
    queries = [rss_feed[x] for x in indices]
    return queries

if __name__ == "__main__":
    #ldamodel=models.ldamodel.LdaModel.load("models/ldamodel_2")
    #vectmodel = models.Doc2Vec.load("models/twitterModelTrimmed.model")
    print("Loaded Models")
    dudebrochill = "data/dudebrochill"
    artistrickards = "data/artistrickards"
    laytechs = "data/laytechs"
    lovetoedit = "data/lovetoeditfilm"
    web20builders = "data/web20builders"
    srfider = "data/surfider"




    rss_url = "https://news.google.com/?output=rss&num=100"
    user_text = "data/temp"
    queries =get_queries(5, user_text, rss_url, vectmodel, ldamodel)
    print([x.title for x in queries])

        
        


