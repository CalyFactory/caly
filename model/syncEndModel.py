from common.util import utils
from manager import db_manager

#eventModel
def setSyncEnd(account_hashkey):
	return db_manager.query(
				"INSERT INTO SYNC_END " 
				"(account_hashkey) "
				"VALUES "
				"(%s) ",
				(			
					account_hashkey,
				)
			)

			