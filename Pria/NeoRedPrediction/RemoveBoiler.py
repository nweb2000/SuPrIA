import util
import Constants
import os
import json
from bs4 import BeautifulSoup
from boilerpipe.extract import Extractor
import copy

def writeBoilerJson(jsonData, downloadDate):
    result = False
    try:
        write_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,
                                       Constants.GOOGLE_LINKS_DIR,downloadDate)
        if not os.path.exists(write_directory):
                    os.makedirs(write_directory)
        outfile = open(os.path.join(write_directory,Constants.GOOGLENEWS_JSON_FILE), 'w')
        json.dump(jsonData, outfile)
        outfile.close()
        result = True   
    except Exception, e:
        util.logger.error("Exception at writing Boiler recomm json for : %s" % downloadDate)
    return result

def readBoilerJson(downloadDate):
    jsonData = None
    try:
        readDirectory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.GOOGLE_LINKS_DIR
                                         ,downloadDate,Constants.GOOGLENEWS_JSON_FILE)
        if os.path.isfile(readDirectory) is True:
             with open(readDirectory) as json_data:
                json_text = json_data.read()
                jsonData = json.loads(json_text)
                json_data.close()
    except Exception, e:
        util.logger.error("Exception at read Boiler recomm json for : %s" % downloadDate)
    return jsonData

def remove_boiler(htmlD):
    extractor = Extractor(extractor='DefaultExtractor', html=htmlD)
    text=extractor.getText().encode('ascii', 'ignore').decode('ascii')
    return text

def BoilerSuggNews(downloadDate):
    jsonData = readBoilerJson(downloadDate)
    if jsonData is None:
        return False
    result = False
    read_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.GOOGLE_NEWS_DIR,downloadDate, 
                                  Constants.SUGG_GOOGLENEWS)
    write_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.BOILER_GOOGLE_NEWS_DIR,
                                   downloadDate, Constants.SUGG_GOOGLENEWS)

    if not os.path.exists(read_directory):
        util.logger.error("Boilers sugg news can't be run because folder isn't present = "+downloadDate)
        return result
    if not os.path.exists(write_directory):
            os.makedirs(write_directory)
    
    suggGoogle = jsonData['suggestGoogle']
    googleLinks = suggGoogle[Constants.GOOGLE]
    finalJson = {'GoogleNews' : jsonData['GoogleNews'], 'suggestGoogle' :{Constants.GOOGLE:[]}}
    count = 0
    for linkObj in googleLinks:
        download = linkObj['download']
        htmlFile = linkObj['id']
        if download == 'yes':
            try:
                htmlData = util.readFromFile(os.path.join(read_directory,htmlFile))      
                if htmlData is not None:
                    html_filename = os.path.join(write_directory,htmlFile)
                    if os.path.isfile(html_filename) is False:
                        htmlText = remove_boiler(htmlData)
                        result = util.writeToFile(htmlText, html_filename) 
                        if result == True:
                            linkObj['content'] = htmlText
                        soup = BeautifulSoup(htmlData, 'html.parser')
                        if soup.title and soup.title.contents[0]:
                              title = soup.title.contents[0]
                        else:
                              title = ""
                        linkObj['title'] = title
                    else:
                        result = True
                    if result == True:
                        count = count + 1
                        util.logger.info('Boilered done for sugg_news ='+html_filename+str(count))
            except Exception, e:
                util.logger.error( "Exception at boiler for google news : %s" % read_directory)
        else:
            pass
        finalJson['suggestGoogle'][Constants.GOOGLE].append(linkObj)

    result = writeBoilerJson(finalJson, downloadDate )
    if result == True:
        util.saveSettings(Constants.LAST_BOILER_SUGGGOOGLENEWS, downloadDate)
        util.logger.info("Sugg Google news boilered for ="+downloadDate+" links="+str(count)+ "total ="+str(len(googleLinks)))
    else:
        util.logger.error("Sugg Google news failed to boilered for ="+downloadDate+" links="+str(count))
    return result    
    
def BoilerNews(downloadDate):
    jsonData = readBoilerJson(downloadDate)
    if jsonData is None:
        return False
    result = False
    read_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.GOOGLE_NEWS_DIR,downloadDate, 
                                  Constants.GOOGLENEWS)
    write_directory = os.path.join(Constants.ROOT_FOLDER,Constants.RECOMMENDATION_DIR,Constants.BOILER_GOOGLE_NEWS_DIR,
                                   downloadDate, Constants.GOOGLENEWS)

    if not os.path.exists(read_directory):
        util.logger.error("Boilers  news can't be run because folder isn't present = "+downloadDate)
        return result
    if not os.path.exists(write_directory):
            os.makedirs(write_directory)
    
    Google = jsonData['GoogleNews']
    googleLinks = Google[Constants.GOOGLE]
    finalJson = {'GoogleNews' : {Constants.GOOGLE:[]}, 'suggestGoogle' : jsonData['suggestGoogle']}
    count = 0
    for linkObj in googleLinks:
        download = linkObj['download']
        htmlFile = linkObj['id']
        if download == 'yes':
            try:
                htmlData = util.readFromFile(os.path.join(read_directory,htmlFile))      
                if htmlData is not None:
                    html_filename = os.path.join(write_directory,htmlFile)
                    if os.path.isfile(html_filename) is False:
                        htmlText = remove_boiler(htmlData)
                        result = util.writeToFile(htmlText, html_filename) 
                        if result == True:
                            linkObj['content'] = htmlText
                        soup = BeautifulSoup(htmlData, 'html.parser')
                        if soup.title and soup.title.contents[0]:
                              title = soup.title.contents[0]
                        else:
                              title = ""
                        linkObj['title'] = title
                    else:
                        result = True
                    if result == True:
                        count = count + 1
                        util.logger.info('Boilered done for sugg_news ='+html_filename+str(count))
            except Exception, e:
                util.logger.error( "Exception at boiler for google news : %s" % read_directory)
        else:
            pass
        finalJson['GoogleNews'][Constants.GOOGLE].append(linkObj)

    result = writeBoilerJson(finalJson, downloadDate )
    if result == True:
        util.saveSettings(Constants.LAST_BOILER_GOOGLENEWS, downloadDate)
        util.logger.info("Google news boilered for ="+downloadDate+" links="+str(count)+ "total ="+str(len(googleLinks)))
    else:
        util.logger.error("Google news failed to boilered for ="+downloadDate+" links="+str(count))
    return result    


def BoilerData(downloadDate):
    ret = False
    read_directory = os.path.join(Constants.ROOT_FOLDER,Constants.DATA_DIR,downloadDate)
    write_directory = os.path.join(Constants.ROOT_FOLDER,Constants.BOILER_DATA_DIR,downloadDate)
    if not os.path.exists(read_directory):
        util.logger.error("Boilers data can't be run because folder isn't present = "+downloadDate)
        return ret
    if not os.path.exists(write_directory):
            os.makedirs(write_directory)
    
    onlyfiles = [ f for f in os.listdir(read_directory) if os.path.isfile(os.path.join(read_directory,f)) ]  
    count = 0      
    for htmlFile in onlyfiles:
            try:
                htmlData = util.readFromFile(os.path.join(read_directory,htmlFile))
                html_filename = os.path.join(write_directory,htmlFile)
                if os.path.isfile(html_filename) is False:
                    htmlText = remove_boiler(htmlData)
                    result = util.writeToFile(htmlText, html_filename) 
                else:
                    result = True
                if result == True:
                    count = count + 1
                util.logger.info('Boilered data done for ='+html_filename+str(count))
            except Exception, e:
                util.logger.error("Exception at boiler for data : " + read_directory + "/"+htmlFile)
    util.saveSettings(Constants.LAST_BOILER_DATA_DIR, downloadDate)
    util.logger.info("datadir boilered for ="+downloadDate+" links="+str(count) + "total ="+str(len(onlyfiles)))
    ret = True
    return ret
        
def RemoveBoiler():
     

     todayDate = util.getTodayDateFolder()
     lastSuggNewsBoiled = util.loadSettings(Constants.LAST_BOILER_SUGGGOOGLENEWS)
     lastNewsBoiled = util.loadSettings(Constants.LAST_BOILER_GOOGLENEWS)
     lastDataBoiled = util.loadSettings(Constants.LAST_BOILER_DATA_DIR)
     
     if lastNewsBoiled:
         util.logger.info("Google news last boiled for ="+lastNewsBoiled)
     else:
         util.logger.info("Google news last boiled for None")
     
     if lastSuggNewsBoiled:
         util.logger.info("Sugg Google news last boiled for ="+lastSuggNewsBoiled)
     else:
         util.logger.info("Sugg Google news last boiled for None")
     
     if lastDataBoiled:
         util.logger.info("data last boiled for ="+lastDataBoiled)
     else:
         util.logger.info("data last boiled for = None")
         
     boilerNewsStatus = True
     boilerSuggNewsStatus = True
     boilerDataStatus = True
     
     #Check whether today links have been extracted or not
     if lastNewsBoiled != todayDate:
         boilerNewsStatus = BoilerNews(todayDate)
     else:
         util.logger.info("Boiler news already done for today :" + todayDate)
         
     #Check whether today sugg links have been extracted or not
     if lastSuggNewsBoiled != todayDate:
         boilerSuggNewsStatus = BoilerSuggNews(todayDate)
     else:
         util.logger.info("Sugg Boiler news already done for today :" + todayDate)
      
     trainingFolders = util.findTrainingDays()  
     anyTrainingFolderBoiled = True
     trainingDoneForDays = 0
     if lastDataBoiled == trainingFolders[0]:
         util.logger.info("Boiler data already done for today :" + lastDataBoiled)
     else:
         anyTrainingFolderBoiled = False
         folderIndex = 0
         if lastDataBoiled != None:
             try:
                 folderIndex = trainingFolders.index(lastDataBoiled) 
                 anyTrainingFolderBoiled = True
             except Exception,e:
                folderIndex = Constants.MAX_PREVIOUS_DAYS 
         else:
             folderIndex = Constants.MAX_PREVIOUS_DAYS
         if folderIndex < 0:
             folderIndex = 0
             util.logger.info("Boiler data for none of the last %d days have been downloaded" % Constants.TRAINING_DAY)
         for folder in range(folderIndex - 1, -1, -1):   
                if   trainingDoneForDays == Constants.TRAINING_DAY:
                    break              
                boilerDataStatus = BoilerData(trainingFolders[folder])
                if boilerDataStatus == False:
                    util.logger.error("Boiler data not done for today :" + trainingFolders[folder])
                else:
                    anyTrainingFolderBoiled = True
                    trainingDoneForDays = trainingDoneForDays + 1
    
     return boilerNewsStatus & boilerSuggNewsStatus & anyTrainingFolderBoiled
    
    