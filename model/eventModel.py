from common.util import utils
from manager import db_manager

#eventModel
def getCaldavUserAccount(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location):
	return db_manager.query(
					"INSERT INTO EVENT " 
					"(event_hashkey,calendar_hashkey,event_id,summary,start_dt,end_dt,created_dt,updated_dt,location) "
					"VALUES "
					"(%s, %s, %s, %s, %s, %s, %s, %s, %s) ",
					(			
						event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location
					)
				)
			