from common.util import utils
from manager import db_manager

#eventModel
def setSync(calendar_id,syncToken):
	return db_manager.query(
				"INSERT INTO sync " 
				"(calendar_id,sync_token,ctime) "
				"VALUES "
				"(%s, %s, now()) ",
				(			
					calendar_id,syncToken
				)
			)
			