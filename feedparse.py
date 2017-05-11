import feedparser
from bs4 import BeautifulSoup
    
# Function grabs the rss feed headlines (titles) and returns them as a list
def getRssFeed(rss_url):
    rss_items = []
    d = feedparser.parse(rss_url)
    for i in d.entries:
        title = i.title 
        link = i.link
        soup = BeautifulSoup(i.description)
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
 

if __name__ == "__main__":
    print(getRssFeed("https://news.google.com/?output=rss&num=100"))
