from common.util import utils
from manager import db_manager
#login_manager
def getCaldavUserAccount(u_id,login_platform):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERACCOUNT "
						"WHERE user_id = %s  AND login_platform = %s"
						,
						(u_id,login_platform) 						
				)
			)

def getUserAccountPlatform(u_id,login_platform):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * FROM USERACCOUNT "
						"WHERE user_id = %s  AND login_platform = %s"
						,
						(u_id,login_platform) 						
				)
			)
def updateCaldavUserAccount(u_id,u_pw,login_platform):
	return db_manager.query(
						"""
						UPDATE USERACCOUNT
						SET access_token = %s,
						is_active = 1
						WHERE user_id = %s and login_platform = %s
						"""
						,
						(u_pw,u_id,login_platform) 						
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
					
def getUserLoginPlatform(apikey):
	return utils.fetch_all_json(
				db_manager.query(
						"""
						SELECT login_platform FROM USERACCOUNT
						LEFT JOIN USERDEVICE on USERDEVICE.account_hashkey = USERACCOUNT.account_hashkey
						WHERE apikey = %s

						"""
						,
						(apikey,) 						
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
def getUserAccountForSync(apikey,user_id,login_platform):	
	return utils.fetch_all_json(
				db_manager.query(
						"""
						SELECT * FROM USERACCOUNT
						WHERE user_hashkey IN(
						SELECT user_hashkey FROM USERACCOUNT
						INNER JOIN USERDEVICE on USERACCOUNT.account_hashkey = USERDEVICE.account_hashkey
						WHERE apikey  = %s
						)
						and user_id = %s and login_platform = %s

						"""
						,
						(apikey,user_id,login_platform) 						
				)			
			)		

def updateUserAccessToken(access_token,new_access_token,google_expire_time):
	return db_manager.query(
						"""
						UPDATE USERACCOUNT 
						SET access_token = %s, 
						google_expire_time = %s 
						WHERE access_token = %s 
						"""
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
def getIsActive(apikey):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT USERACCOUNT.is_active FROM USERACCOUNT 
					LEFT JOIN USERDEVICE on USERACCOUNT.account_hashkey = USERDEVICE.account_hashkey 
					WHERE USERDEVICE.apikey = %s
					"""
					,
					(apikey,)
				)
			)	
#해당 apikey를 가지는 계정과 연동된 모든 계정의 account_hashkey를 가져온다. account_hashkey에 해당하는 active 를 1로바꿔줄것이다.
def getUserAccountWithApikey(apikey):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT USERACCOUNT.user_hashkey FROM USERACCOUNT
					INNER JOIN 
					(SELECT USERACCOUNT.user_hashkey FROM USERACCOUNT
					INNER JOIN USERDEVICE ON USERACCOUNT.account_hashkey = USERDEVICE.account_hashkey
					WHERE USERACCOUNT.is_active is not null and apikey = %s) as needActiveUser
					ON needActiveUser.user_hashkey = USERACCOUNT.user_hashkey
					GROUP BY USERACCOUNT.user_hashkey

					"""
					,
					(apikey,)
				)
			)		
def getAnotherConnectionUser(user_hashkey,u_id):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT * FROM USERACCOUNT 
					WHERE user_hashkey = %s AND user_id != %s AND is_active is not null
					""" 
					,
					(user_hashkey,u_id)
				)
			)	
	
def updateIsActiveWithUserHasheky(user_hashkey,is_active):
	return 	db_manager.query(
				"""
                   UPDATE USERACCOUNT
                    SET is_active = %s
                    WHERE user_hashkey = %s
				"""
				,
				(			
					is_active,user_hashkey
				)
			)


def withdrawWithAccountHashkey(account_hashkey):
	return 	db_manager.query(
				"""
				UPDATE USERACCOUNT 
				SET user_id = "None",
				access_token = "None",
				caldav_homeset = NULL,
				is_active = NULL,
				subject = NULL,
				refresh_token = NULL
				WHERE account_hashkey  = %s 
				"""
				,
				(			
					account_hashkey,
				)
			)

def withdraw(user_hashkey):
	return 	db_manager.query(
				"""
				UPDATE USERACCOUNT 
				SET user_id = "None",
				access_token = "None",
				caldav_homeset = NULL,
				is_active = NULL,
				subject = NULL,
				refresh_token = NULL
				WHERE user_hashkey  = %s 
				"""
				,
				(			
					user_hashkey,
				)
			)
def getAccessToken(account_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT access_token FROM USERACCOUNT 
					WHERE account_hashkey = %s 
					"""
					,
					(account_hashkey,)
				)
			)		