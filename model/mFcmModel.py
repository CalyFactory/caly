from common.util import utils
from manager import mongo_manager
from bson.json_util import dumps

fcm = mongo_manager.fcm

def findAllFcm():
    return dumps(fcm.find())     

def insertFcm(json):
    return fcm.insert(json)
