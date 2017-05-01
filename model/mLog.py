from common.util import utils
from manager import mongo_manager
from bson.json_util import dumps
from common.util.statics import *
from model import userDeviceModel
from datetime import datetime

def getUserInfo(apikey):
	result = {}
	user = userDeviceModel.getUserWithApikey(apikey)
	account_hashkey = user[0]['account_hashkey']
	user_id = user[0]['user_id']
	login_platform = user[0]['login_platform']

	result['user_id'] = user_id
	result['login_platform'] = login_platform
	result['apikey'] = apikey
	result['account_hashkey'] = account_hashkey	

	return result


def findAllLog(typee):
	if typee == MONGO_COLLECTION_EVENT_LOG:
		collection = mongo_manager.event_log
	
	elif typee == MONGO_COLLECTION_RECO_LOG:
		collection = mongo_manager.reco_log

	elif typee == MONGO_COLLECTION_ACCOUNT_LIST_LOG:
		collection = mongo_manager.account_list_log

	
	return dumps(collection.find()) 

def insertLog(typee,json):
	if typee == MONGO_COLLECTION_EVENT_LOG:
		collection = mongo_manager.event_log
		
	elif typee == MONGO_COLLECTION_RECO_LOG:
		collection = mongo_manager.reco_log
	
	elif typee == MONGO_COLLECTION_ACCOUNT_LIST_LOG:
		collection = mongo_manager.account_list_log	

	# currentTime
	json['cTime'] = datetime.now()

	return collection.insert(json)
