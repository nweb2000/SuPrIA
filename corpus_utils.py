#################################
#
# Collection of methods for preprocessing corpus
#
################################
from gensim.models.doc2vec import TaggedDocument
from nltk import word_tokenize
import re


def stopwords(filename="stopwords.txt"):
    """
    Return list of stop words
    """
    return [line.strip() for line in open(filename)] + ['...']

def punc():
    return [",",".","'", '"', ":", "?", "`", "~", ";", "(", ")", "-", "+", "=", "<", ">", "[", "]", "{", "}", "&", "#", "*", "!"]


def normalize(sent):
    """
    Perform normalization pipeline on sentence given (as string of text)
    and return list of words 
    """
    return [word for word in word_tokenize(sent.lower()) if word not in stopwords() and word not in punc() and len(word) > 2]


def clean_tweet(tweet):
    tweet = re.sub(r'https?://[^\s]+[\s]', '', tweet) #remove retweets and other users
    tweet = re.sub(r'@[^\s]+[\s]', '', tweet)
    return tweet

def remove_stopwords(infile_name, outfile_name):
   infile = TwitterCorpusGen(infile_name)
   outfile = open(outfile_name, 'w')

#   for i in infile:
    

    
class TwitterCorpusGen:
    def __init__(self, filename):
        self.filename=filename

    def __iter__(self):
        doc=""
        num = 0
        for id, line in enumerate(open(self.filename)):
            split = line.split(',')
            user = split[0]
            d = ",".join(split[1:])
            data = eval(d)
            for t in data: #data for a single user
                tweet = t.split('|')[3]
                tweet = clean_tweet(tweet)

                #words = [word for word in word_tokenize(tweet.lower()) if word not in stopwords() and word not in punc() and len(word) > 2]
                words = [word for word in tweet.lower().split()]
#            print(words)
                label = [user]
                yield TaggedDocument(words, label)

class SingleUserTwitterGen:
    def __init__(self, filename):
        self.filename=filename

    def get_tweets(self):
        doc=""
        num = 0
        for line in open(self.filename):
            split = line.split(',')
            user = split[0]
            d = ",".join(split[1:])
            data = eval(d)
            twitter_data = ""
            for t in data: #data for a single user
                tweet = t.split('|')[3]
                tweet = clean_tweet(tweet)
                twitter_data = twitter_data + " " + tweet

                #words = [word for word in word_tokenize(tweet.lower()) if word not in stopwords() and word not in punc() and len(word) > 2]

            words = [word for word in twitter_data.lower().split()]
            return words

    def get_tweets2(self):
        doc=""
        num = 0
        for line in open(self.filename):
            split = line.split(',')
            user = split[0]
            d = ",".join(split[1:])
            data = eval(d)
            twitter_data = ""
            for t in data: #data for a single user
                tweet = t.split('|')[3]
                tweet = clean_tweet(tweet)
                twitter_data = twitter_data + "\n" + tweet

                #words = [word for word in word_tokenize(tweet.lower()) if word not in stopwords() and word not in punc() and len(word) > 2]

            return twitter_data 

    def __iter__(self):
        doc=""
        num = 0
        for id,line in enumerate(open(self.filename)):
            split = line.split(',')
            user = split[0]
            d = ",".join(split[1:])
            data = eval(d)
            twitter_data = ""
            for t in data: #data for a single user
                tweet = t.split('|')[3]
                tweet = clean_tweet(tweet)
                twitter_data = twitter_data + tweet

                #words = [word for word in word_tokenize(tweet.lower()) if word not in stopwords() and word not in punc() and len(word) > 2]
            words = [word for word in twitter_data.lower().split()]
#            print(words)
            label = [user]
            yield TaggedDocument(words, label)


#for NOW corpus
class ModernCorpusGen:
    def __init__(self, filename):
        self.filename=filename

    def __iter__(self):
        doc=""
        num = 0
        stopword = stopwords()
        pun = punc()
        for line in open(self.filename):
            doc = re.sub(r'@[0-9]+[\s]', '', line)
            words = [word for word in word_tokenize(doc.lower()) if word not in stopwords() and word not in punc() and len(word) > 2]
#            print(words)
            yield words



#for nyt
class CorpusGen:
    def __init__(self, filename):
        self.filename=filename

    def __iter__(self):
        doc=""
        num = 0
        stopword = stopwords()
        pun = punc()
        for id, line in enumerate(open(self.filename)):
            if line[0:2] == '||':
           #     print(doc + "\n")
           #     words = [word for word in word_tokenize(doc.lower()) if word not in stopwords() and word not in punc() and len(word) > 2] #remeber to do preprocessing
           #     words = [word for word in doc.lower().split() if word not in stopword and word not in pun and len(word) > 2] #remeber to do preprocessing
                words = [word for word in doc.lower().split()] #remeber to do preprocessing
           #     print(words)
                label = ["DOC_%s" % num]
                doc = ""
                num = num + 1
                yield TaggedDocument(words, label)
            else:
                doc = doc + " " + line
                

            

            
