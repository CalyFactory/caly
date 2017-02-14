from manager import db_manager
from caldavclient import CaldavClient
from common.util import utils

def updateCal():
	client = CaldavClient(
	    'https://caldav.calendar.naver.com/principals/users/kkk1140' ,
	    'kkk1140',
	    'tkdaud123'
	)

	principal = client.getPrincipal()
	homeset = principal.getHomeSet()
	calendars = homeset.getCalendars()


	arrQueryString = []
	arrQueryString.append('INSERT INTO CALENDAR (calendar_hashkey,account_hashkey,calendar_id,calendar_name,caldav_calendar_url,caldav_ctag) values ')
	for calendar in calendars:
		calendar_hashkey = utils.makeHashKey(calendar.calendarId)
		account_hashkey = '49a854d2ae9b0635a01e23e47a2aadf7d80e49284466183674c1d5b9'
		arrQueryString.append('("'+ calendar_hashkey +'","'+ account_hashkey + '","' + calendar.calendarId + '","'+ calendar.calendarName+'","'+calendar.calendarUrl+'","'+calendar.cTag+ '")')
		arrQueryString.append(',')

	arrQueryString.pop()
	lastQuery = "".join(arrQueryString)

	print('string=>'+str(lastQuery))

	# db_manager.query(
	# 						"SELECT * FROM USERACCOUNT WHERE subject = %s "
	# 						,
	# 						(subject,) 						
	# # 				)	
	db_manager.query(
						lastQuery
							
					)					
