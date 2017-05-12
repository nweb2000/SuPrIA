import sys
import os
from sys import platform as _platform
def root_path():
    path = sys.executable
    listPath = path.split("/")
    #windows default
    splitIndex = 1
    if _platform == "darwin":
        splitIndex = 5
    listPath = listPath[:-splitIndex]
    return "/".join(listPath)


NEDREAD = "NeoRedPrediction"
MIN_GOOGLELINKS_DAILY = 20
#ROOT_FOLDER = "/Users/neocfc/Documents/LatestApp/Mac"
ROOT_FOLDER = root_path()
RECOMMENDATION_DIR ="Recommendation_Dir"
LINKS_DIR ="linksDir"
LOG_DIR = "Log"
DATA_DIR = "dataDir"
FACEBOOK_DIR = "facebookDir"
TWITTER_DIR = "twitterDir"
ENGINE_DIR = "engineDir"
RELEVANCE_FILE = "relevance.json"
SMOOTHNESS_FILE = "smoothness.json"
CLARITY_FILE = "clarity.json"
RECOMMINFO_FILE = "recomminfo.json"
GOOGLENEWS = "GoogleNews"
SUGG_GOOGLENEWS = "SuggGoogleNews"
GOOGLENEWS_JSON_FILE = "GoogleNews.json"
GOOGLE_LINKS_DIR ="Google_Links_Dir"
GOOGLE_NEWS_DIR ="Google_News_Dir"
GOOGLE_LINKS_FILE = "Google_Links_File"
BOILER_GOOGLE_NEWS_DIR = "Boiler_Google_News_Dir"
BOILER_DATA_DIR = "Boiler_Data_Dir"
FINAL_DIR = "Final_dir"
FEEDBACK_DIR = "Feedback_dir"
URL_DIR = "Url_dir"
ULTIMATE_FILE = "ultimate.json"
LOG_FILE = "prediction_log.txt"
LAST_GOOGLENEWS_DOWNLOAD = "LAST_GOOGLENEWS_DOWNLOAD"
LAST_GOOGLELINKS_DOWNLOAD = "LAST_GOOGLELINKS_DOWNLOAD"
LAST_BOILER_GOOGLENEWS = "LAST_BOILER_GOOGLENEWS"
LAST_BOILER_SUGGGOOGLENEWS = "LAST_BOILER_SUGGGOOGLENEWS"
LAST_BOILER_DATA_DIR = "LAST_BOILER_DATA_DIR"
LAST_RELEVANCE_DIR = "LAST_RELEVANCE_DIR"
LAST_SUGG_RELEVANCE_DIR = "LAST_SUGG_RELEVANCE_DIR"
LAST_SUGG_SMOOTHNESS_DIR = "LAST_SUGG_SMOOTHNESS_DIR"
LAST_SMOOTHNESS_DIR = "LAST_SMOOTHNESS_DIR"
LAST_SUGG_CLARITY_DIR = "LAST_SUGG_CLARITY_DIR"
LAST_CLARITY_DIR = "LAST_CLARITY_DIR"
LAST_SUGG_RECOMMENDATION_DONE = "LAST_SUGG_RECOMMENDATION_DONE"
LAST_RECOMMENDATION_DONE = "LAST_RECOMMENDATION_DONE"
MAX_PREVIOUS_DAYS = 15
TRAINING_DAY = 5
RECOMMENDED_LINKS = 40
BASELINE = "baseline"
GOOGLE = "google"
GRAPH = "graph"
NERGRAPH = "nergraph"
MAX_FILES_SMOOTHNESS = 200