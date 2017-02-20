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
def setGoogleUserAccount(account_hashkey,user_hashkey,login_platform,u_id,access_token,google_expire_time,subject):
	return 	db_manager.query(
					"INSERT INTO USERACCOUNT " 
					"(account_hashkey,user_hashkey,login_platform,user_id,access_token,google_expire_time,subject)"
					"VALUES"
					"(%s, %s, %s, %s, %s, %s, %s)",
					(			
						account_hashkey,
						user_hashkey,
						login_platform,
						u_id,
						access_token,
						google_expire_time,
						subject
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
