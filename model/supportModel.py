from common.util import utils
from manager import db_manager

def getNotice():
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT notice_title,notice_description,create_datetime "
					"FROM NOTICE "
					,
					()
				)		
			)		
def setRequests(apikey,account_hashkey,contents):
	return db_manager.query(
				"INSERT INTO REQUESTS (apikey,account_hashkey,contents) "
				"VALUES(%s,%s,%s)"
				,
				(apikey,account_hashkey,contents)
			)		
			
