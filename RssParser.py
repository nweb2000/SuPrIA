import feedparser
from bs4 import BeautifulSoup
    
# Function grabs the rss feed headlines (titles) and returns them as a list
def getRssFeed(rss_url):
    rss_items = []
    d = feedparser.parse(rss_url)
    for i in d.entries:
        title = i.title 
        link = i.link
        soup = BeautifulSoup(i.description, "lxml")
        description = soup.text
        rss_items.append(RssHeadline(link, title,description))
    return rss_items
             
 

class RssHeadline:
    def __init__(self, link, title, description):
        self.link = link
        self.title = title
        self.descrip = description

    def __str__(self):
        return "{} | {} | {}".format(self.link, self.title, self.descrip)
 

#if __name__ == "__main__":
def all_cat():    
    categories = {'Top Stories':"https://news.google.com/?cf=all&num=40&ned=us&output=rss", 
                  'Technology':"https://news.google.com/?num=40&cf=all&topic=tc&output=rss", 
                  'Entertainment':"https://news.google.com/?cf=all&num=40&topic=e&output=rss", 
                  'Sports':"https://news.google.com/?num=40&cf=all&topic=s&output=rss", 
                  'Science':"https://news.google.com/?num=40&cf=all&topic=snc&output=rss", 
                  'Business':"https://news.google.com/?cf=all&num=40&topic=b&output=rss",
                  }
    
    newsFeed = {}
    articles = []
    for topic, url in categories.items():
        feed = getRssFeed(url)
        newsFeed[topic] = feed
        articles.extend(feed)
    
    return articles
#    for news, values in newsFeed.items():
#    print(news)
#    for stories in values:
#        print(stories)
