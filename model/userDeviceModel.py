from common.util import utils
from manager import db_manager

#login_manager
def getUserDeviceWithUuid(uuid):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERDEVICE WHERE uuid = %s "
						,
						(uuid,) 						
				)
			)	
	
#login_manager
def setUserDevice(device_hashkey,account_hashkey,apikey):
	return db_manager.query(
				"INSERT INTO USERDEVICE " 
				"(device_hashkey,account_hashkey,apikey)"
				"VALUES"
				"(%s, %s, %s)",
				(			
					device_hashkey,
					account_hashkey,
					apikey
				)
			)		
#login_manager			
def updateUserApikey(apikey,uuid):
	return db_manager.query(
						"UPDATE USERDEVICE " 
						"SET apikey = %s, " 
						"is_active = 1 "
						"WHERE uuid = %s"
						,
						(apikey,uuid) 						
				)		

#member
def setGoogleUserDevice(device_hashkey,account_hashkey,apikey,push_token,device_type,app_version,device_info,uuid,sdkLevel):
	return 	db_manager.query(
					"INSERT INTO USERDEVICE " 
					"(device_hashkey,account_hashkey,apikey,push_token,device_type,app_version,device_info,uuid,sdkLevel)"
					"VALUES"
					"(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
					(			
						device_hashkey,
						account_hashkey,
						apikey,
						push_token,
						device_type,
						app_version,
						device_info,
						uuid,
						sdkLevel
					)
				)
#registerDevice
def getUserHashkey(apikey):
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT user_hashkey from USERDEVICE " +				
					"INNER JOIN USERACCOUNT on USERDEVICE.account_hashkey = USERACCOUNT.account_hashkey " +					
					"WHERE USERDEVICE.apikey = %s "
					,
					(									
						apikey,
					)
				)		
			)	
#registerDevice
def updateUserDevice(push_token,device_type,app_version,device_info,uuid,sdkLevel,apikey,):
	return db_manager.query(
					"UPDATE USERDEVICE " +				
					"SET push_token = %s, " +
					"device_type = %s, " +
					"app_version = %s, " +
					"device_info = %s, " +
					"uuid = %s, " +
					"sdkLevel = %s " +
					"WHERE apikey = %s "

					,
					(									
						push_token,
						device_type,
						app_version,
						device_info,
						uuid,
						sdkLevel,
						apikey

					)
				)		
			
#updatePushtoken
def updatePushToken(push_token,apikey):
	return db_manager.query(
					"UPDATE USERDEVICE SET push_token = %s " 
					"WHERE apikey = %s "
					,
					(			
						push_token,
						apikey,						
					)
				)	
#logout				
def logout(apikey):
	return 	db_manager.query(
					"UPDATE USERDEVICE " 
					"SET apikey = null, is_active = 0 "
					"WHERE apikey = %s",
					(									
						apikey,						
					)
				)	
def setVersion(apikey,app_version):
	return 	db_manager.query(
					"UPDATE USERDEVICE " 
					"SET app_version = %s "
					"WHERE apikey = %s",
					(									
						app_version,apikey					
					)
				)	
def setSdkLevel(apikey,sdkLevel):
	return 	db_manager.query(
					"UPDATE USERDEVICE " 
					"SET sdkLevel = %s "
					"WHERE apikey = %s",
					(									
						sdkLevel,apikey					
					)
				)

def getPushToken(apikey):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT push_token "
						+ "FROM USERDEVICE "
						+ "WHERE apikey = %s "
						,
						(apikey,) 						
				)
			)	


def setRecviePush(apikey,value):
	return 	db_manager.query(
					"UPDATE USERDEVICE " 
					"SET receive_push = %s "
					"WHERE apikey = %s",
					(									
						value,apikey,					
					)
				)

