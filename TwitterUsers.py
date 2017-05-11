
# coding: utf-8

# In[7]:

print("Hello")


# In[8]:

import re


# In[9]:

with open("tweets2009-06.txt", encoding='utf8') as file:
    head = [next(file) for x in range(150)]
total = int(re.search(r'\d+', head[0]).group())


# In[10]:

print(head[0])


# In[2]:

from collections import defaultdict
import re
count = 0
userDict = defaultdict(list)
with open("tweets2009-06.txt", encoding='utf8') as file:
        for line in file:
            if (line.startswith('total number')):
                #get total number of tweets in the file
                total = int(re.search(r'\d+', line).group())
            elif (line.startswith('T\t')):
                #Timestamp of tweet
                time = line[2:-1]
            elif (line.startswith('U\t')):            
                #User Account Information
                check = line.split('/')
                user = check[len(check)-1][:-1]
            elif (line.startswith('W\t')):
                #Extract url if it exists at the end of the tweet.
                match = re.search("(?P<url>https?://[^\s]+)", line)
                if match :
                    match = match.group("url")
                else :
                    match = "NoURL"
                #Body of the tweet
                body = line[:-1]
            else:
                #Write to dictionary
                count = count + 1
                output = str(count)+"|"+str(time)+"|"+match+"|"+body+"\n"
                userDict[user].append(output)
        
        print("Writing to File")
        f = open("Twitterati/tweetsByUser.txt", "a+", encoding='utf8')
        for (k,v) in userDict.items():
            f.write(str(k)+","+str(v)+"\n")
        f.close()


# In[5]:

with open("Twitterati/tweetsByUser.txt", encoding='utf8') as file:
    head = [next(file) for x in range(100)]
print(head) 


# In[ ]:



