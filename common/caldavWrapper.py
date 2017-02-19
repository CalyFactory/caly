from manager import db_manager
from caldavclient import CaldavClient
from common.util import utils


def getCalDavClient(login_platform,u_id,u_pw):
	if login_platform == 'naver':		
		hostname = 'https://caldav.calendar.naver.com/principals/'
	elif login_platform == 'ical':
		hostname = 'https://caldav.icloud.com/'

	#클라에서 loginState확인을 거쳐온 id/pw임으로 무조건 인증된 정보이다.
	calDavclient = CaldavClient(
	    hostname,
	    (u_id,u_pw)
	)
	
	return calDavclient;
		