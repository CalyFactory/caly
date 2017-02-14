from common.util import utils
from manager import db_manager

def getUserDeviceWithSessionkey(sessionkey):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERDEVICE WHERE session_key = %s "
						,
						(sessionkey,) 						
				)
			)	


def getUserDeviceWithUuid(uuid):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERDEVICE WHERE uuid = %s "
						,
						(uuid,) 						
				)
			)	

def setGoogleUserDevice(device_hashkey,account_hashkey,session_key,uuid):
	return db_manager.query(
				"INSERT INTO USERDEVICE " 
				"(device_hashkey,account_hashkey,session_key,uuid)"
				"VALUES"
				"(%s, %s, %s, %s)",
				(			
					device_hashkey,
					account_hashkey,
					session_key,
					uuid
				)
			)
	

def setUserDevice(device_hashkey,account_hashkey,session_key):
	return db_manager.query(
				"INSERT INTO USERDEVICE " 
				"(device_hashkey,account_hashkey,session_key)"
				"VALUES"
				"(%s, %s, %s)",
				(			
					device_hashkey,
					account_hashkey,
					session_key
				)
			)		
			
def updateUserDeviceLogout(session_key,uuid):
	return db_manager.query(
						"UPDATE USERDEVICE " +
						"SET session_key = %s " +
						"WHERE uuid = %s"
						,
						(sessionkey,uuid) 						
				)		