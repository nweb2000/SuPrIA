
from ConfigParser import SafeConfigParser
import graphConstants
import time
import logging
import os 
import datetime
import re
import nltk
import string
import traceback
from datetime import date, timedelta
from sys import platform as _platform
import random

packageName = "com.neoRed.prediction.settings"
config = None
logger = None
stopwords = None


def initLogger():
    global logger
    logger = logging.getLogger('neoRed')
    todayDateFolder = getTodayDateFolder()
    log_dir = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.GRAPH_DIR,graphConstants.LOG_DIR,graphConstants.NEDREAD,todayDateFolder)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir,graphConstants.LOG_FILE)
    if os.path.isfile(log_file) == False:
         file = open(log_file,'w')   # Trying to create a new file or open one
         file.close()
         
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)
    if _platform != "darwin":
        f=open(os.path.join(graphConstants.ROOT_FOLDER,'main_windows_run.bat'),'r')
        fileText=f.read()
        lines = (fileText).split("\n")
        env_txt = re.findall('"([^"]*)"', lines[1])
        env_all = env_txt[0].split("\\")
        env = "\\".join(env_all[:-1])
        print "javahome= " + env
        os.environ["JAVAHOME"] = env
        os.environ["JAVA_HOME"] = env
        pass
        
def initStopWordsList():
    global stopwords
    stopwords = []
    f=open(os.path.join(graphConstants.ROOT_FOLDER,'stopwords.txt'),'r')
    fileText=f.read()
    for word in fileText.split('\n'):
        stopwords.append(word)
    f.close()
    f=open(os.path.join(graphConstants.ROOT_FOLDER,'hipwords.txt'),'r')
    fileText=f.read()
    for word in fileText.split('\n'):
        stopwords.append(word)
    f.close()
    f=open(os.path.join(graphConstants.ROOT_FOLDER,'uselesswords.txt'),'r')
    fileText=f.read()
    for word in fileText.split('\n'):
        stopwords.append(word)
    f.close()
    pass
def initGlobal():
    initStopWordsList()

def extract_text(filehtml):
    filetext = filehtml.encode('utf-8')
    filetext = re.sub(r'[^\x00-\x7F]+', ' ', filetext)
    filetext = filetext.lower()

    # remove the punctuation

    no_punctuation = filetext.translate(None, string.punctuation)
    filetext=re.sub("[^a-zA-Z]+", " ", no_punctuation)
    filetext=re.sub(r'\W*\b\w{1,3}\b', ' ', filetext)
    tokens = nltk.word_tokenize(filetext)
    filtered = [w for w in tokens if not w in stopwords]
    return filtered

def findCorpus(onlyfiles):
     corpus = []
     for obj in onlyfiles:
         filehtml = open(obj, 'r')
         try:
             head, tail = os.path.split(obj)
             if tail != '.DS_Store':
                 text = filehtml.read()
                 text = extract_text(text)
                 corpus.append(text)

         except Exception:
             print traceback.format_exc()
         finally:
            if filehtml:
                filehtml.close()
     return corpus
def initSettings():
    global config
    config = SafeConfigParser()
    config.read('config.ini')
    if not config.has_section("main"):
        config.add_section("main")
    
    
def saveSettings(key, value):
    global config
    config.set('main', key, value)
    with open('config.ini', 'w') as f:
        config.write(f)  
def loadSettings(key):
    value = None
    if config.has_option("main",key):
       value = config.get("main",key)
    return value
def getTodayDateFolder():
    today = time.strftime("%Y-%m-%d")
    #return "2016-02-14"
    return today
def getDateFolder(date):
    day = date.strftime("%Y-%m-%d")
    return day
def getYesterdayDateFolder():
    yesterday = date.today() - timedelta(1)
    str_yesterday = yesterday.strftime("%Y-%m-%d")
    #return "2016-02-13"
    return str_yesterday

def findTrainingDays():
    today = datetime.date.today()
    training = []
    delta = datetime.timedelta(days=1)
    for i in range(graphConstants.MAX_PREVIOUS_DAYS):
        yesterday = today - delta
        yester_str = getDateFolder(yesterday)
        training.append(yester_str)
        today = yesterday
    return training
def findTrainingFiles():
    onlyfiles = []
    completed_days = 0
    day_found = False
    dates = findTrainingDays()
    for day in dates:
        if completed_days == graphConstants.TRAINING_DAY:
            break
        folders = []
        day_found = False
        folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.BOILER_DATA_DIR,day))
        folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.DATA_DIR,day,graphConstants.FACEBOOK_DIR))
        folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.DATA_DIR,day, graphConstants.TWITTER_DIR))
        for files_dir in folders:
            if os.path.exists(files_dir):
                day_found = True
                onlyfiles.extend([os.path.join(files_dir,
                     fi) for fi in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir,
                     fi))])
        if day_found == True:
           completed_days = completed_days + 1 
    return onlyfiles

def findGraphFiles():
    onlyfiles = []
    graphFileNames = []
    last_day = loadSettings(graphConstants.date_LAST_GRAPH_DONE)
    #last_day = "11-08-2015"
    date_YesterdayFolder = getYesterdayDateFolder()
    delta = datetime.timedelta(days=1)
    if last_day == None:
        onlyfiles = findTrainingFiles()
    else:    
        while last_day != date_YesterdayFolder:
            folders = []
            currentDay = datetime.datetime.strptime(last_day,"%Y-%m-%d") + delta
            last_day = currentDay.strftime("%Y-%m-%d")
            folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.BOILER_DATA_DIR,last_day))
            
            #folders.append(os.path.join(Constants.ROOT_FOLDER,Constants.DATA_DIR,last_day,Constants.FACEBOOK_DIR))
            #folders.append(os.path.join(Constants.ROOT_FOLDER,Constants.DATA_DIR,last_day, Constants.TWITTER_DIR))
            for files_dir in folders:
                if os.path.exists(files_dir):
                    onlyfiles.extend([os.path.join(files_dir,
                         fi) for fi in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir,
                         fi))])
                
    for files in onlyfiles:
        if _platform == "darwin":
            splitFile = files.split("/")
        else:
            splitFile = files.split("\\")
        graphFileNames.append(splitFile[-1]+"_"+splitFile[-2])
    return onlyfiles, graphFileNames

def findGraphNERFiles():
    onlyfiles = []
    graphFileNames = []
    last_day = loadSettings(graphConstants.date_LAST_GRAPHNER_DONE)
    #last_day = "11-08-2015"
    date_YesterdayFolder = getYesterdayDateFolder()
    delta = datetime.timedelta(days=1)
    if last_day == None:
        onlyfiles = findTrainingFiles()
    else:    
        while last_day != date_YesterdayFolder:
            folders = []
            currentDay = datetime.datetime.strptime(last_day,"%Y-%m-%d") + delta
            last_day = currentDay.strftime("%Y-%m-%d")
            folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.BOILER_DATA_DIR,last_day))
            
            #folders.append(os.path.join(Constants.ROOT_FOLDER,Constants.DATA_DIR,last_day,Constants.FACEBOOK_DIR))
            #folders.append(os.path.join(Constants.ROOT_FOLDER,Constants.DATA_DIR,last_day, Constants.TWITTER_DIR))
            for files_dir in folders:
                if os.path.exists(files_dir):
                    onlyfiles.extend([os.path.join(files_dir,
                         fi) for fi in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir,
                         fi))])
                
    for files in onlyfiles:
        if _platform == "darwin":
            splitFile = files.split("/")
        else:
            splitFile = files.split("\\")
        graphFileNames.append(splitFile[-1]+"_"+splitFile[-2])
    return onlyfiles, graphFileNames

def findRecommTrainGraphFiles():
    onlyfiles = []
    graphFileNames = []
    last_day = loadSettings(graphConstants.date_LAST_GRAPH_DONE)
    completed_days = 0
    day_found = False
    dates = findTrainingDays()
    for day in dates:
        if day > last_day:
            logger.info("Last day for graph training file = "+day)
            break
        if completed_days == graphConstants.TRAINING_DAY:
            logger.info("Last day for graph training file = "+day)
            break
        folders = []
        day_found = False
        folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.BOILER_DATA_DIR,day))
        #folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.DATA_DIR,day,graphConstants.FACEBOOK_DIR))
        #folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.DATA_DIR,day, graphConstants.TWITTER_DIR))
        for files_dir in folders:
            if os.path.exists(files_dir):
                day_found = True
                onlyfiles.extend([os.path.join(files_dir,
                     fi) for fi in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir,
                     fi))])
        if day_found == True:
           completed_days = completed_days + 1 
           
    onlyfiles = random_select(onlyfiles)
    for files in onlyfiles:
        if _platform == "darwin":
            splitFile = files.split("/")
        else:
            splitFile = files.split("\\")
        graphFileNames.append(splitFile[-1]+"_"+splitFile[-2])
    return onlyfiles, graphFileNames

def findRecommTrainGraphNerFiles():
    onlyfiles = []
    graphFileNames = []
    last_day = loadSettings(graphConstants.date_LAST_GRAPH_DONE)
    completed_days = 0
    day_found = False
    dates = findTrainingDays()
    for day in dates:
        if day > last_day:
            logger.info("Last day for ner graph training file = "+day)
            break
        if completed_days == graphConstants.TRAINING_DAY:
            logger.info("Last day for ner graph training file = "+day)
            break
        folders = []
        day_found = False
        folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.BOILER_DATA_DIR,day))
        #folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.DATA_DIR,day,graphConstants.FACEBOOK_DIR))
        #folders.append(os.path.join(graphConstants.ROOT_FOLDER,graphConstants.DATA_DIR,day, graphConstants.TWITTER_DIR))
        for files_dir in folders:
            if os.path.exists(files_dir):
                day_found = True
                onlyfiles.extend([os.path.join(files_dir,
                     fi) for fi in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir,
                     fi))])
        if day_found == True:
           completed_days = completed_days + 1 
    onlyfiles = random_select(onlyfiles)
    for files in onlyfiles:
        if _platform == "darwin":
            splitFile = files.split("/")
        else:
            splitFile = files.split("\\")
        graphFileNames.append(splitFile[-1]+"_"+splitFile[-2])
    return onlyfiles, graphFileNames

def findRecommFiles():
    onlyfiles = []
    graphFileNames =[]
    day = getTodayDateFolder()
    folders = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.RECOMMENDATION_DIR,graphConstants.BOILER_GOOGLE_NEWS_DIR,day, graphConstants.GOOGLENEWS)
    if os.path.exists(folders):
        onlyfiles.extend([os.path.join(folders,
                     fi) for fi in os.listdir(folders) if os.path.isfile(os.path.join(folders,
                     fi))])
    for files in onlyfiles:
        if _platform == "darwin":
            splitFile = files.split("/")
        else:
            splitFile = files.split("\\")
        graphFileNames.append(graphConstants.TYPE_GOOGLE+"_"+splitFile[-1]+"_"+splitFile[-3])
    return onlyfiles, graphFileNames
    
def findSuggRecommFiles():
    onlyfiles = []
    graphFileNames =[]
    day = getTodayDateFolder()
    folders = os.path.join(graphConstants.ROOT_FOLDER,graphConstants.RECOMMENDATION_DIR,graphConstants.BOILER_GOOGLE_NEWS_DIR,day, graphConstants.SUGG_GOOGLENEWS)
    if os.path.exists(folders):
        onlyfiles.extend([os.path.join(folders,
                     fi) for fi in os.listdir(folders) if os.path.isfile(os.path.join(folders,
                     fi))])
    for files in onlyfiles:
        if _platform == "darwin":
            splitFile = files.split("/")
        else:
            splitFile = files.split("\\")
        graphFileNames.append(graphConstants.TYPE_SUGG+"_"+splitFile[-1]+"_"+splitFile[-3])
    return onlyfiles, graphFileNames
def EtoFloat(val):
    text = "{:.50f}".format(float(val[0]/val[1]))
    text_f = float(text)
    return text_f

def random_select(Corpus):
     random.shuffle(Corpus)
     return Corpus[:graphConstants.MAX_FILES_SMOOTHNESS]