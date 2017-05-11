from gensim.models import Doc2Vec
import corpus_utils

#data = corpus_utils.CorpusGen("data/tweetsByUser.txt")
#data = corpus_utils.CorpusGen("data/testdata")
#model = Doc2Vec(size=50, window=5)
#model = Doc2Vec(size=100, window=5, min_count=2, iter=5)
#model.build_vocab(data)
#model.train(data, total_words=4106148, epochs=model.iter )
#model.train(data, total_words=252139686, epochs=model.iter )
#model.save("twitterPredict.model")
#model.train(data)
#a = model.docvecs[0]
#b = model.docvecs[1]
#c = model.docvecs[2]
##print(model.docvecs.most_similar(positive=[a]))
#print(model.docvecs.most_similar(positive=[b]))
#print(model.docvecs.most_similar(positive=[c]))


data = corpus_utils.TwitterCorpusGen("data/tweetsByUser.txt")
#data = corpus_utils.CorpusGen("data/testdata")
#model = Doc2Vec(size=50, window=5)
model = Doc2Vec(size=300, window=5, min_count=2, iter=5)
model.build_vocab(data)
model.intersect_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True)
#model.train(data, total_words=4106148, epochs=model.iter )
model.train(data, total_words=252139686, epochs=model.iter )
model.save("twitterPredict.model")
#model.train(data)
a = model.docvecs[0]
b = model.docvecs[1]
c = model.docvecs[2]
print(model.docvecs.most_similar(positive=[a]))
print(model.docvecs.most_similar(positive=[b]))
print(model.docvecs.most_similar(positive=[c]))
