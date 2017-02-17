from common.util import utils
from manager import db_manager

#eventModel
def setEvents(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location):
	return db_manager.query(
								"INSERT INTO EVENT " 
								"(event_hashkey,calendar_hashkey,event_id,summary,start_dt,end_dt,created_dt,updated_dt,location) "
								"VALUES "
								"(%s, %s, %s, %s, %s, %s, %s, %s, %s) ",
								(			
									event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location
								)
							)

def updateEvents(summary,start_date,end_date,created,updated,location,event_id):
	return db_manager.query(
								"UPDATE EVENT set " 								
								"summary = %s, "
								"start_dt = %s, "
								"end_dt = %s, "
								"created_dt = %s, "
								"updated_dt = %s, "
								"location = %s "
								"where event_id = %s",
								(			
									summary,start_date,end_date,created,updated,location,event_id
								)
							)

def deleteEvents(event_id):
	return db_manager.query(
								"DELETE from EVENT " 								
								"where event_id = %s",
								(			
									event_id,
								)
							)

#오늘날자부터 과거 
def getEvents(user_hashkey,pager,rangee):

	return utils.fetch_all_json(				
				db_manager.query(
					"SELECT EVENT.created_dt,EVENT.end_dt,CALENDAR.calendar_name,EVENT.event_hashkey,EVENT.recurrance,EVENT.start_dt,EVENT.summary "+
					"FROM USERACCOUNT " +							
					"INNER JOIN CALENDAR ON USERACCOUNT.account_hashkey = CALENDAR.account_hashkey "+
					"INNER JOIN EVENT on CALENDAR.calendar_hashkey = EVENT.calendar_hashkey " +
					"WHERE start_dt < CURDATE() AND user_hashkey = %s " +
					"ORDER BY start_dt " +
					"limit %s,%s",
					(			
						user_hashkey,pager,rangee
					)
				)

			)
