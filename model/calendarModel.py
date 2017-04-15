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

def setGoogleCalendar(calendars,account_hashkey,arr_channel_id):
	arrQueryString = []
	arrQueryString.append('INSERT INTO CALENDAR (calendar_hashkey,account_hashkey,calendar_id,calendar_name,google_channel_id) values ')
	
	for idx, calendar in enumerate(calendars):

		calendar_hashkey = utils.makeHashKey(calendar['id'])
		calendar_channelId = utils.makeHashKey(calendar_hashkey)

		arrQueryString.append('("'+ calendar_hashkey +'","'+ account_hashkey + '","' + calendar['id'] + '","'+ calendar['summary']+'","'+arr_channel_id[idx]+'")')
		arrQueryString.append(',')

	arrQueryString.pop()
	lastQuery = "".join(arrQueryString)

	return db_manager.query(
						lastQuery							
					)			
def withdraw(account_hashkey):
	return 	db_manager.query(
				"""
				UPDATE CALENDAR 
				SET caldav_calendar_url = NULL,
				is_active = NULL
				WHERE account_hashkey = %s 
				"""
				,
				(			
					account_hashkey,
				)
			)	

def getCalendar(channel_id):
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT * FROM CALENDAR WHERE google_channel_id = %s",(channel_id,)
				)		
			)		

def getAccountHashkey(channel_id):			
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT access_token,CALENDAR.account_hashkey from CALENDAR INNER JOIN USERACCOUNT on CALENDAR.account_hashkey = USERACCOUNT.account_hashkey WHERE CALENDAR.google_channel_id = %s "					
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


def getAllCalendarWithAccountHashkey(account_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * from CALENDAR "
						"where account_hashkey = %s "
						,
						(account_hashkey,) 						
				)
			)			

#푸시등록요청한것들 찾기
def getGoogleSyncState(account_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT * from CALENDAR "+
						"where account_hashkey = %s "+
						"AND google_sync_state > 1"
						,
						(account_hashkey,) 						
				)
			)
def getGoogleCalendarInfo(apikey):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT USERACCOUNT.access_token,CALENDAR.google_channel_id,CALENDAR.google_resource_id,CALENDAR.google_expiration FROM USERDEVICE 
					LEFT JOIN CALENDAR on USERDEVICE.account_hashkey = CALENDAR.account_hashkey
					LEFT JOIN USERACCOUNT on USERDEVICE.account_hashkey = USERACCOUNT.account_hashkey
					WHERE apikey = %s AND google_sync_state = 3					
					"""
						,
						(apikey,) 						
				)
			)	
def getGoogleCalendarInfoWithAccountHashkey(account_hashkey):
	return utils.fetch_all_json(
				db_manager.query(
					"""
					SELECT USERACCOUNT.access_token,CALENDAR.google_channel_id,CALENDAR.google_resource_id,CALENDAR.google_expiration FROM USERDEVICE 
					LEFT JOIN CALENDAR on USERDEVICE.account_hashkey = CALENDAR.account_hashkey
					LEFT JOIN USERACCOUNT on USERDEVICE.account_hashkey = USERACCOUNT.account_hashkey
					WHERE CALENDAR.account_hashkey = %s AND CALENDAR.google_sync_state = 3					
					"""
						,
						(account_hashkey,) 						
				)
			)		
def updateGoogleSyncState(channel_id,state):
	return db_manager.query(
				"UPDATE CALENDAR SET google_sync_state = %s WHERE google_channel_id = %s"
				,(state,channel_id)
			)

def updateGoogleExpiration(channel_id,google_expiration,resource_id):
	return db_manager.query(
				"""
				UPDATE CALENDAR 
				SET google_expiration = %s,
				google_resource_id = %s
				WHERE google_channel_id = %s
				"""
				,(google_expiration,resource_id,channel_id)
			)	
def updateCalendarRecoState(calendar_hashkey,reco_state):
	return db_manager.query(
				"UPDATE CALENDAR SET reco_state= %s WHERE calendar_hashkey = %s"
				,(reco_state,calendar_hashkey)
			)

def deleteCalendarList(account_hashkey):
	return db_manager.query(
			"DELETE FROM CALENDAR WHERE account_hashkey = %s"
			,
			(account_hashkey,)
		)


def getRetachGoogleWatchList():
	return utils.fetch_all_json(
				db_manager.query(
						"""
						SELECT * FROM CALENDAR 
						LEFT JOIN USERACCOUNT on USERACCOUNT.account_hashkey = CALENDAR.account_hashkey
						WHERE google_expiration <= date(adddate(now(),INTERVAL 1 DAY)) 
						AND google_expiration >= now()
						AND google_sync_state = 3
						AND USERACCOUNT.is_active = 1						
						"""
						,
						() 						
				)
			)				
