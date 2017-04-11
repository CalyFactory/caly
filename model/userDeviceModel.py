
from common.util import utils
from manager import db_manager

#login_manager
def getUserDeviceWithUuid(uuid,login_platform):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT *FROM USERDEVICE
					LEFT JOIN USERACCOUNT on USERDEVICE.account_hashkey = USERACCOUNT.account_hashkey
					where uuid = %s and login_platform = %s					
					"""	
						,
						(uuid,login_platform) 						
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
def updateUserApikey(apikey,account_hashkey):
	return db_manager.query(
						"UPDATE USERDEVICE " 
						"SET apikey = %s, " 
						"is_active = 1 "
						"WHERE account_hashkey = %s"
						,
						(apikey,account_hashkey) 						
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
#login_manager
def getUserDeviceWithAccountHashkey(account_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT * FROM USERDEVICE
					WHERE account_hashkey = %s
					"""
					,
					(account_hashkey,)
				)
			)	
#login_manager
def updateAccountHashkey(account_hashkey,uuid,login_platform,apikey):
	return 	db_manager.query(
					"""
					UPDATE USERDEVICE 
					INNER JOIN USERACCOUNT on USERDEVICE.account_hashkey = USERACCOUNT.account_hashkey
					SET USERDEVICE.account_hashkey = %s,
					USERDEVICE.apikey = %s,
					USERDEVICE.is_active =1 
					WHERE USERDEVICE.uuid = %s and USERACCOUNT.login_platform = %s					
					"""
					,
					(account_hashkey,apikey, uuid,login_platform)
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
def getUserAccountHashkey(apikey):
	return 	utils.fetch_all_json(
				db_manager.query(
					"SELECT account_hashkey FROM USERDEVICE " 					
					"WHERE apikey= %s ",
					(									
						apikey,					
					)
				)
			)
def getUserSyncOlderTime(user_hashkey):
	return 	utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT USERACCOUNT.account_hashkey,ctime FROM USERACCOUNT
					INNER JOIN (
					SELECT account_hashkey,ctime FROM SYNC_END WHERE sync_time_state = 2
					) as synEnd
					on synEnd.account_hashkey = USERACCOUNT.account_hashkey
					WHERE user_hashkey = %s

					"""
					,
					(									
						user_hashkey,					
					)
				)
			)	
def getUserApikeyList(user_hashkey):
	return 	utils.fetch_all_json(
				db_manager.query(
					"SELECT apikey FROM USERACCOUNT " 					
					"LEFT JOIN USERDEVICE on USERACCOUNT.account_hashkey = USERDEVICE.account_hashkey "
					"WHERE user_hashkey = %s "
					,
					(									
						user_hashkey,					
					)
				)
			)	


def deleteUserDeviceAll(user_hashkey):
	return 	db_manager.query(
					"DELETE USERDEVICE FROM USERDEVICE " 					
					"LEFT JOIN USERACCOUNT on USERACCOUNT.account_hashkey = USERDEVICE.account_hashkey "
					"WHERE user_hashkey = %s"
					,
					(									
						user_hashkey,					
					)
				)
def withdraw(account_hashkey):
	return 	db_manager.query(
				"""
				UPDATE USERDEVICE 
				SET push_token = NULL,
				is_active = NULL,
				uuid = NULL
				WHERE account_hashkey = %s 
				"""
				,
				(			
					account_hashkey,
				)
			)	
