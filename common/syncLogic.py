import logging
from flask.views import MethodView
import flask

from common.util import utils

from model import userDeviceModel
from model import userAccountModel
from model import userModel
from model import calendarModel
from model import eventModel
from model import syncModel
from model import syncEndModel

from common import caldavWrapper
from common import gAPI
from manager import network_manager

import json
import urllib
from datetime import timedelta,datetime
from pytz import timezone

from manager.redis import redis
from common.util.statics import *
import time

def caldav(user,user_hashkey,login_platform):

	logging.info('sync! caldav!')

	u_id = user[0]['user_id']
	u_pw = user[0]['access_token']
	account_hashkey = user[0]['account_hashkey']			
	
	calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)

	principal = calDavclient.getPrincipal()
	homeset = principal.getHomeSet()
	calendars = homeset.getCalendars()

	#캘린더 해시키를 먼저 만든다.
	arr_calendar_hashkey = []
	for calendar in calendars:
		calendar_hashkey = utils.makeHashKey(calendar.calendarId)
		arr_calendar_hashkey.append(calendar_hashkey)
	try:
		calendarModel.setCaldavCalendar(calendars,account_hashkey,arr_calendar_hashkey)
	except Exception as e:
	    return utils.syncState(SYNC_CALDAV_ERR_SET_CALENDAR,str(e))
	
	logging.debug('hashkey = >' + str(arr_calendar_hashkey))

	for idx,calendar in enumerate(calendars):
	    
	    logging.debug('calnedarsss=> ' + calendar.calendarName)
		
	    ##TODO
	    ##RANGE를 현재시간부터 5개월후로!
	    range_start = time.strftime("%Y%m%dT000000Z")
	    range_end = datetime.now()+ timedelta(hours=3600)
	    range_end = datetime.strftime(range_end, "%Y%m%dT000000Z") 	
	    logging.info('range_start ==> '+range_start)
	    logging.info('range_edn ==> '+range_end)

	    eventList = calendar.getEventByRange( "20170301T000000Z", "20170729T000000Z")				    
	    eventDataList = calendar.getCalendarData(eventList)
	    calendar_hashkey = arr_calendar_hashkey[idx]

	    for event_set in eventDataList:		
		    logging.debug('eventset => ' + str(event_set.eventData))
		    event = event_set.eventData['VEVENT']		    
		   	#만약 Transparet인 이벤트라면 다음 루프로 넘어간다.
		    if 'TRANSP' in event:
		        if event['TRANSP'] == 'TRANSPARENT':
		            continue

		    # #uid를 eventId로 쓰면되나
		    event_id = event_set.eventId
		    event_hashkey = utils.makeHashKey(event_id)
		    # eventurl은 무엇을 저장해야되나여
		    caldav_event_url = event_set.eventUrl
		    #etag는 어디서 얻을수 있죠?
		    caldav_etag = event_set.eTag
		    summary = None
		    if 'SUMMARY' in event:
		    	summary = event['SUMMARY']

		    
		    start_dt = None
		    end_dt = None

		    if 'DTSTART' in event:			

		    	start_dt = event['DTSTART']
		    	# datetime일경우만
		    	if(isinstance(start_dt,datetime)):
		    		#한국시간으로바꿔준다
		    		start_dt = start_dt.astimezone(timezone('Asia/Seoul'))

		    if 'DTEND' in event:
		    	end_dt = event['DTEND']
		    	if(isinstance(end_dt,datetime)):
		    		#한국시간으로바꿔준다
		    		end_dt = end_dt.astimezone(timezone('Asia/Seoul'))					  
		    
		    #타임존 라이브러리정하기
		    created_dt = event['CREATED']
		    if(isinstance(created_dt,datetime)):
			    created_dt =created_dt.astimezone(timezone('Asia/Seoul'))					  		    
		    #문자열을 날짜시간으로 변경해줌. 
		    # created_dt = datetime.strptime(created_dt, "%Y%m%dT%H%M%S") + timedelta(hours=9)	    


		    if 'LAST-MODIFIED' in event:
		    	updated_dt = event['LAST-MODIFIED']
	
		    if(isinstance(updated_dt,datetime)):
		    		#한국시간으로바꿔준다
			    updated_dt =updated_dt.astimezone(timezone('Asia/Seoul'))					  		    		    	
		        
		    else:		
			    updated_dt = created_dt
		    if event['LOCATION'] == '':
		    	location = 'noLocation'
		    else:
		    	location = event['LOCATION']

		    logging.debug('hashkey=>' + calendar_hashkey)	
		    logging.debug('event_hashkey=>' + event_hashkey)	
		    logging.debug('event_id=>' + event_id)	
		    logging.debug('caldav_event_url=>' + caldav_event_url)	
		    logging.debug('caldav_etag=>' + caldav_etag)	
		    logging.debug('summary=>' + summary)
		    logging.debug('start_dt=>' + str(start_dt))
		    logging.debug('end_dt=>' + str(end_dt))
		    logging.debug('created_dt=>' + str(created_dt))
		    logging.debug('updated_dt=>' + str(updated_dt))
		    logging.debug('location=>' + str(location))
		    
		    try:
		        eventModel.setCaldavEvents(event_hashkey,calendar_hashkey,event_id,summary,start_dt,end_dt,created_dt,updated_dt,location,caldav_event_url,caldav_etag)
		    except Exception as e:
			    return utils.syncState(SYNC_CALDAV_ERR_SET_EVENTS,str(e))

		#캘린더마다 싱크된 타임을 기록해준다. 
	    try:
		    syncModel.setSync(calendar_hashkey,'null')
	    except Exception as e:
		    return utils.syncState(SYNC_CALDAV_ERR_SET_SYNC_TIME,str(e))

	try:
		syncEndModel.setSyncEnd(account_hashkey)
	except Exception as e:
		return utils.syncState(SYNC_CALDAV_ERR_SET_SYNC_END,str(e))

	return utils.syncState(SYNC_CALDAV_SUCCESS,None)

def google(user,apikey):	
	utils.checkTime(datetime.now(),'start')
	

	access_token = user[0]['access_token']
	account_hashkey = user[0]['account_hashkey']

	calendar_list_URL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
	calendar_list = json.loads(network_manager.reqGET(calendar_list_URL,access_token))
	
	logging.debug('calendarList=>' + str(calendar_list)	)
	
	calendars = calendar_list['items']


	# #디비에 array로 다이렉트로 넣기위한 코드.
	arr_channel_id = []
	for calendar in calendars:
		calendar_channelId = utils.makeHashKey(calendar['id'])		
		arr_channel_id.append(calendar_channelId)		
	# logging.debug('channl=> ' + str(arr_channel_id))
			
	try:
		#최초 googlepushcomplete 가 0
		calendarModel.setGoogleCalendar(calendars,account_hashkey,arr_channel_id)
	except Exception as e:
		return utils.syncState(SYNC_GOOGLE_ERR_SET_CALENDAR,str(e))		

	calendarsInDB = calendarModel.getAllCalendarWithAccountHashkey(account_hashkey)

	#1. 첫째로 캘린더에있는 캘린더들을 돌려서 디비에 이벤트를 저장한다.
	#TODO
	#maxResults가 최대 몇개까지인지 확인하고 최대로 가져온다.
	#RANGE를 현재시간부터 5개월후로!
	#key가 opqaue인것부터
	range_start = time.strftime("%Y-%m-%dT00:00:00-09:00")
	range_end = datetime.now()+ timedelta(hours=3600)
	range_end = datetime.strftime(range_end, "%Y-%m-%dT00:00:00-09:00") 	

	for calendar in calendarsInDB:
		logging.info('[timeTest]calendar ForLoop==> '+str(utils.checkTime(datetime.now(),'ing')))
		body = {
					'maxResults': 1000,
					'timeMin':range_start,
					'timeMax':range_end					
				}	
		reqEventsList(apikey,calendar,user,body)

		#캘린더 id가 일반계정이면==>무조건 push를 받음으로 pushStart로 설정해준다.
		calendar_id = calendar['calendar_id']
		calendar_channel_id = calendar['google_channel_id']
		if '@gmail.com' in calendar_id or '@naver.com' in calendar_id or '@ical.com' in calendar_id or '@group.calendar.google.com' in calendar_id:
			calendarModel.updateGoogleSyncState(calendar_channel_id,GOOGLE_SYNC_STATE_PUSH_START)			

	logging.info('[timeTest]end All event Save==> '+str(utils.checkTime(datetime.now(),'ing')))			
	#notification 저장하기.
	#기존 state가 ==0 이고 이 요청을 보낸상태면 1로 바꿘준다.
	#watch에서 받았으면 2로 값을바꾸고 push Notification을 보낸다.
	for idx, calendar in enumerate(calendars):
		logging.info('[timeTest]watch Request==> '+str(utils.checkTime(datetime.now(),'ing')))			
		logging.debug('calender id =>'+calendar['id'])		
		calendar_id = calendar['id']
		if '@gmail.com' in calendar_id or '@naver.com' in calendar_id or '@ical.com' in calendar_id or '@group.calendar.google.com' in calendar_id:
			watch_URL = 'https://www.googleapis.com/calendar/v3/calendars/'+calendar['id']+'/events/watch'
			body = {
				"id" : arr_channel_id[idx],
				"type" : "web_hook",
				"address" : "https://ssoma.xyz:55566/v1.0/sync/watchReciver",
				"token" : apikey
			}						
			res = network_manager.reqPOST(watch_URL,access_token,body)
			#start push noti
	
			logging.info('ress=s==> '+str(res))
		#codeReview
		#status code 를 202등으로 바꾼다.
	return utils.syncState(SYNC_GOOGLE_SUCCES,None)

def reqEventsList(apikey,calendar,user,body={}):

	channel_id = calendar['google_channel_id']
	account_hashkey = calendar['account_hashkey']
	access_token = user[0]['access_token']
	calendar_hashkey = calendar['calendar_hashkey']
	calendar_id = calendar['calendar_id']

	URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events?'
	
	res = json.loads(network_manager.reqGET(URL,access_token,body))

	logging.info('calendarResponse'+str(res))
	# logging.info('itemLenth'+str(len(res['items'])))
	for item in res['items']:
		
		# logging.debug('event_id=>'+str(item['id']))

		event_id = item['id']		
		summary = 'noTitle'
		start_date = None
		end_date = None
		created = None
		updated = None
		location = 'noLocation'

		if 'summary' in item:			
			summary = item['summary']
		if 'location' in item:
			location = item['location']

		if 'created' in item:												
			created = str(item['created'])[:-5]
			created = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=9)	    
		if 'updated' in item:
			updated = str(item['updated'])[:-5]		
			updated = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=9)	    


		if 'date' in item['start']:					
			start_date = item['start']['date']
			end_date = item['end']['date']

		elif 'dateTime' in item['start']:		
			start_date = utils.date_utc_to_current(str(item['start']['dateTime']))
			end_date = utils.date_utc_to_current(str(item['end']['dateTime']))


		event_hashkey = utils.makeHashKey(event_id)
		eventModel.setGoogleEvents(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location)
	logging.info('[timeTest]cnt= '+str(len(res['items']))+'setEVENTS==> '+str(utils.checkTime(datetime.now(),'ing')))



	#넥스트 토큰이있을경우 없을때까지 요청을 보낸다.

	range_start = time.strftime("%Y-%m-%dT00:00:00-09:00")
	range_end = datetime.now()+ timedelta(hours=3600)
	range_end = datetime.strftime(range_end, "%Y-%m-%dT00:00:00-09:00") 	
	logging.info('range_start ==> '+range_start)
	logging.info('range_edn ==> '+range_end)
	if 'nextPageToken' in res:
		
		body = {
					'maxResults': 1000,
					'timeMin':range_start,
					'timeMax':range_end,					
					'pageToken' : str(res['nextPageToken'])
				}
		reqEventsList(apikey,calendar,user,body)

	else :
		
		

		syncToken = res['nextSyncToken']
		logging.debug('syncToken==>'+syncToken)

		#해당캘린더의 싱크가 끝낫다+> syncToken을 저장해둔다.
		syncModel.setSync(calendar_hashkey,syncToken)
		#캘린 더 해시키에 해당하는 googlePushComplete 1로만든다.
		calendarModel.updateGoogleSyncState(channel_id,GOOGLE_SYNC_STATE_EVENTS_END)
 

