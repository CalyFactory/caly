from common.util import utils
from manager import db_manager
#login_manager
def getCaldavUserAccount(u_id,u_pw):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERACCOUNT WHERE user_id = %s AND access_token = %s "
						,
						(u_id,u_pw) 						
				)
			)
#login_manager	
def getGoogleUserAccount(subject):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERACCOUNT WHERE subject = %s "
						,
						(subject,) 						
				)			
			)	
#member
def setCaldavUserAccount(account_hashkey,user_hashkey,login_platform,u_id,u_pw,caldav_homeset):
	return 	db_manager.query(
					"INSERT INTO USERACCOUNT " 
					"(account_hashkey,user_hashkey,login_platform,user_id,access_token,caldav_homeset)"
					"VALUES"
					"(%s, %s, %s, %s, %s, %s)",
					(			
						account_hashkey,
						user_hashkey,
						login_platform,
						u_id,
						u_pw,
						caldav_homeset
					)
				)			

#member
def setGoogleUserAccount(account_hashkey,user_hashkey,login_platform,u_id,access_token,google_expire_time,subject,refresh_token):
	return 	db_manager.query(
					"INSERT INTO USERACCOUNT " 
					"(account_hashkey,user_hashkey,login_platform,user_id,access_token,google_expire_time,subject,refresh_token)"
					"VALUES"
					"(%s, %s, %s, %s, %s, %s, %s, %s)",
					(			
						account_hashkey,
						user_hashkey,
						login_platform,
						u_id,
						access_token,
						google_expire_time,
						subject,
						refresh_token
					)
				)			

						

#sync						
def getUserAccount(user_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERACCOUNT WHERE user_hashkey = %s "
						,
						(user_hashkey,) 						
				)			
			)	

def getUserAccountWithAccessToken(access_token):	
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERACCOUNT WHERE access_token = %s "
						,
						(access_token,) 						
				)			
			)	

def updateUserAccessToken(access_token,new_access_token,google_expire_time):
	return db_manager.query(
						"UPDATE USERACCOUNT " 
						"SET access_token = %s, " 
						"google_expire_time = %s "
						"WHERE access_token = %s "
						,
						(new_access_token,google_expire_time,access_token) 						
				)				
def getHasAccountList(user_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT USERACCOUNT.login_platform, USERACCOUNT.user_id, USERACCOUNT.create_datetime FROM USER "
						"INNER JOIN USERACCOUNT ON USER.user_hashkey = USERACCOUNT.user_hashkey "
						"WHERE USER.user_hashkey = %s "
						,
						(user_hashkey,) 						
				)			
			)	