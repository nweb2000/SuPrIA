#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
categories = {'Suggested':"https://news.google.com/news/section?cf=all&pz=1&authuser=1&topic=sfy"}

def download():
    try:
        htmlfile = urllib2.urlopen("https://news.google.com/news/section?cf=all&pz=1&authuser=1&topic=sfy")
        html = htmlfile.read()
        f = open("test.html", 'w')
        f.write(html)
        f.close()
    except Exception, e:
        pass

if __name__ == '__main__':
    download()

            