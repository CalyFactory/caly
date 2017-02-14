from common.util import utils
from manager import db_manager
def getCaldavUserAccount(u_id,u_pw):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERACCOUNT WHERE user_id = %s AND access_token = %s "
						,
						(u_id,u_pw) 						
				)
			)
def getGoogleUserAccount(subject):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERACCOUNT WHERE subject = %s "
						,
						(subject,) 						
				)			
			)	

def setGoogleUserAccount(account_hashkey,user_hashkey,login_platform,u_id,access_token,google_expire_time,subject):
	return db_manager.query(
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
			