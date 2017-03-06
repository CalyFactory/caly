from common.util import utils
from manager import db_manager

#eventModel
def setSyncEnd(account_hashkey,sync_time_state):
	return db_manager.query(
				"INSERT INTO SYNC_END " 
				"(account_hashkey,sync_time_state) "
				"VALUES "
				"(%s,%s) ",
				(			
					account_hashkey,sync_time_state
				)
			)

def getSyncEnd(account_hashkey,sync_time_state):
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT id FROM SYNC_END " 
					"WHERE account_hashkey = %s AND sync_time_state = %s"
					,
					(			
						account_hashkey,sync_time_state
					)
				)
			)

						