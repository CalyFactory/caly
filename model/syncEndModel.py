from common.util import utils
from manager import db_manager

#eventModel
def setSyncEnd(account_hashkey,sync_time_state):
	return db_manager.query(
				"""
				INSERT INTO SYNC_END 
				(account_hashkey,sync_time_state) 
				VALUES 
				(%s,%s) 
				"""
				,
				(			
					account_hashkey,sync_time_state
				)
			)

def getSyncEnd(account_hashkey,sync_time_state):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT id FROM SYNC_END 
					WHERE account_hashkey = %s AND sync_time_state = %s
					"""
					,
					(			
						account_hashkey,sync_time_state
					)
				)
			)

def getAccountLatestSyncTime(apikey):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT USERACCOUNT.login_platform,USERACCOUNT.user_id,synAccount.latestSyncTime FROM  USERACCOUNT
					INNER JOIN(

					SELECT SYNC_END.account_hashkey,max(ctime) as latestSyncTime  FROM SYNC_END
					INNER JOIN (
					SELECT account_hashkey FROM USERACCOUNT
					WHERE user_hashkey IN(
					SELECT user_hashkey FROM USERACCOUNT
					INNER JOIN USERDEVICE on USERACCOUNT.account_hashkey = USERDEVICE.account_hashkey
					WHERE apikey  = %s 					
					AND USERACCOUNT.is_active = 1
					)
					) AS accounts
					ON accounts.account_hashkey = SYNC_END.account_hashkey
					WHERE SYNC_END.sync_time_state = 3 or SYNC_END.sync_time_state = 2					
					GROUP BY account_hashkey
					) as synAccount on synAccount.account_hashkey = USERACCOUNT.account_hashkey
					WHERE USERACCOUNT.is_active = 1			
					"""
					,
					(			
						apikey,
					)
				)
			)
