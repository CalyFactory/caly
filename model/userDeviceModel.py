from common.util import utils
from manager import db_manager
#login_manager
def getUserDeviceWithSessionkey(sessionkey):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERDEVICE WHERE session_key = %s "
						,
						(sessionkey,) 						
				)
			)	

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
def setUserDevice(device_hashkey,account_hashkey,sessionkey):
	return db_manager.query(
				"INSERT INTO USERDEVICE " 
				"(device_hashkey,account_hashkey,session_key)"
				"VALUES"
				"(%s, %s, %s)",
				(			
					device_hashkey,
					account_hashkey,
					sessionkey
				)
			)		
#login_manager			
def updateUserDeviceLogout(sessionkey,uuid):
	return db_manager.query(
						"UPDATE USERDEVICE " +
						"SET session_key = %s " +
						"WHERE uuid = %s"
						,
						(sessionkey,uuid) 						
				)		

#member
def setGoogleUserDevice(device_hashkey,account_hashkey,sessionkey,push_token,device_type,app_version,device_info,uuid):
	return 	db_manager.query(
					"INSERT INTO USERDEVICE " 
					"(device_hashkey,account_hashkey,session_key,push_token,device_type,app_version,device_info,uuid)"
					"VALUES"
					"(%s, %s, %s, %s, %s, %s, %s, %s)",
					(			
						device_hashkey,
						account_hashkey,
						sessionkey,
						push_token,
						device_type,
						app_version,
						device_info,
						uuid
					)
				)
#registerDevice
def getUserHashkey(sessionkey):
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT user_hashkey from USERDEVICE " +				
					"INNER JOIN USERACCOUNT on USERDEVICE.account_hashkey = USERACCOUNT.account_hashkey " +					
					"WHERE USERDEVICE.session_key = %s "
					,
					(									
						sessionkey,
					)
				)		
			)	
#registerDevice
def updateUserDevice(push_token,device_type,app_version,device_info,uuid,sessionkey):
	return db_manager.query(
					"UPDATE USERDEVICE " +				
					"SET push_token = %s, " +
					"device_type = %s, " +
					"app_version = %s, " +
					"device_info = %s, " +
					"uuid = %s " +
					"WHERE session_key = %s "
					,
					(									
						push_token,
						device_type,
						app_version,
						device_info,
						uuid,
						sessionkey
					)
				)		
			
#updatePushtoken
def updatePushToken(push_token,sessionkey):
	return db_manager.query(
					"UPDATE USERDEVICE SET push_token = %s " 
					"WHERE session_key = %s "
					,
					(			
						push_token,
						sessionkey,						
					)
				)	
#logout				
def logout(sessionkey):
	return 	db_manager.query(
					"UPDATE USERDEVICE " 
					"SET session_key = null, is_active = 0 "
					"WHERE session_key = %s",
					(									
						sessionkey,						
					)
				)	
def setVersion(sessionkey,app_version):
	return 	db_manager.query(
					"UPDATE USERDEVICE " 
					"SET app_version = %s "
					"WHERE session_key = %s",
					(									
						app_version,sessionkey					
					)
				)	

