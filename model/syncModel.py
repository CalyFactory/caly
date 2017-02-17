from common.util import utils
from manager import db_manager

#eventModel
def setSync(calendar_hashkey,syncToken):
	return db_manager.query(
				"INSERT INTO SYNC " 
				"(calendar_hashkey,sync_token,ctime) "
				"VALUES "
				"(%s, %s, now()) ",
				(			
					calendar_hashkey,syncToken
				)
			)

			