from common.util import utils
from manager import db_manager
#sync
def setCalendar(calendars,account_hashkey):
	arrQueryString = []
	arrQueryString.append('INSERT INTO CALENDAR (calendar_hashkey,account_hashkey,calendar_id,calendar_name,caldav_calendar_url,caldav_ctag) values ')
	for calendar in calendars:
		calendar_hashkey = utils.makeHashKey(calendar.calendarId)
		arrQueryString.append('("'+ calendar_hashkey +'","'+ account_hashkey + '","' + calendar.calendarId + '","'+ calendar.calendarName+'","'+calendar.calendarUrl+'","'+calendar.cTag+ '")')
		arrQueryString.append(',')

	arrQueryString.pop()
	lastQuery = "".join(arrQueryString)

	print('string=>'+str(lastQuery))
	return db_manager.query(
						lastQuery							
					)		