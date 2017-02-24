from common.util import utils
from manager import db_manager
#sync
def setCaldavCalendar(calendars,account_hashkey,arr_calendar_hashkey):
	arrQueryString = []
	arrQueryString.append('INSERT INTO CALENDAR (calendar_hashkey,account_hashkey,calendar_id,calendar_name,caldav_calendar_url,caldav_ctag) values ')
	for idx,calendar in enumerate(calendars):
		# calendar_hashkey = utils.makeHashKey(calendar.calendarId)
		arrQueryString.append('("'+ arr_calendar_hashkey[idx] +'","'+ account_hashkey + '","' + calendar.calendarId + '","'+ calendar.calendarName+'","'+calendar.calendarUrl+'","'+calendar.cTag+ '")')
		arrQueryString.append(',')

	arrQueryString.pop()
	lastQuery = "".join(arrQueryString)

	print('string=>'+str(lastQuery))
	return db_manager.query(
						lastQuery							
					)		

def setGoogleCalendar(calendars,account_hashkey,arr_channel_id,push_state_before):
	arrQueryString = []
	arrQueryString.append('INSERT INTO CALENDAR (calendar_hashkey,account_hashkey,calendar_id,calendar_name,google_channel_id,google_push_complete) values ')
	
	for idx, calendar in enumerate(calendars):

		calendar_hashkey = utils.makeHashKey(calendar['id'])
		calendar_channelId = utils.makeHashKey(calendar_hashkey)

		arrQueryString.append('("'+ calendar_hashkey +'","'+ account_hashkey + '","' + calendar['id'] + '","'+ calendar['summary']+'","'+arr_channel_id[idx]+'","'+push_state_before +'")')
		arrQueryString.append(',')

	arrQueryString.pop()
	lastQuery = "".join(arrQueryString)

	return db_manager.query(
						lastQuery							
					)			

def getCalendar(channel_id):
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT * FROM CALENDAR WHERE google_channel_id = %s",(channel_id,)
				)		
			)		
def updatePushComplete(channel_id,value):
	return db_manager.query(
				"UPDATE CALENDAR SET google_push_complete = %s WHERE google_channel_id = %s"
				,(value,channel_id,)
			)
def updateEventEnd(channel_id):
	return db_manager.query(
				"UPDATE CALENDAR SET google_push_complete = 3 WHERE google_channel_id = %s"
				,(channel_id,)
			)
def getHashkey(channel_id):			
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT access_token,CALENDAR.account_hashkey from CALENDAR INNER JOIN USERACCOUNT on CALENDAR.account_hashkey = USERACCOUNT.account_hashkey WHERE CALENDAR.google_channel_id = %s"
					,(channel_id,)
				)		
			)		
#sync
def getLatestSyncToken(calendar_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
					"select * from CALENDAR left join SYNC on SYNC.calendar_hashkey = CALENDAR.calendar_hashkey  where SYNC.calendar_hashkey = %s order by SYNC.ctime desc limit 1"
					,(calendar_hashkey,)
				)	
			)	 
def getGooglePushComplete(account_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * from CALENDAR "+
						"where account_hashkey = %s "+
						"AND google_push_complete > 1"
						,
						(account_hashkey,) 						
				)
			)		