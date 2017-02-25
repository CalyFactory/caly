import logging
from flask.views import MethodView
import flask
from flask import session
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
from common import FCM
from manager.redis import redis
from common.util.statics import *

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

	    eventList = calendar.getEventByRange( "20170128T000000Z", "20180223T000000Z")				    
	    eventDataList = calendar.getCalendarData(eventList)
	    calendar_hashkey = arr_calendar_hashkey[idx]

	    for event_set in eventDataList:				    	
		    event = event_set.eventData['VCALENDAR'][0]['VEVENT'][0]
		    logging.debug('eventset => '+str(event_set))
		    
		   
		    # #uid를 eventId로 쓰면되나
		    event_id = event_set.eventId
		    event_hashkey = utils.makeHashKey(event_id)
		    # eventurl은 무엇을 저장해야되나여
		    caldav_event_url = event_set.eventUrl
		    #etag는 어디서 얻을수 있죠?
		    caldav_etag = event_set.eTag
		    summary = event['SUMMARY']
		    print('sum'+summary)
		    start_dt = None
		    end_dt = None

		    ###
		    #FIxME 성민이가 DTSTART가져오는것 처리해주면 이코드는 버릴거야.
		    #레거시할 코드.
		    for key in event:
			    if 'DTSTART' in key:					    	
			    	start_dt = event[key]
			    elif 'DTEND' in key:
			    	end_dt = event[key]
	  
		    
		    #타임존 라이브러리정하기
		    created_dt = event['CREATED'][:-1]
		    #문자열을 날짜시간으로 변경해줌. 
		    created_dt = datetime.strptime(created_dt, "%Y%m%dT%H%M%S") + timedelta(hours=9)	    


		    if 'LAST-MODIFIED' in event:
		        updated_dt = event['LAST-MODIFIED'][:-1]
		        updated_dt = datetime.strptime(updated_dt, "%Y%m%dT%H%M%S") + timedelta(hours=9)
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

def google(user,sessionkey):	
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
	for calendar in calendarsInDB:
		body = {
					'maxResults': 10
				}	
		reqEventsList(sessionkey,calendar,user,body)

		#캘린더 id가 일반계정이면==>무조건 push를 받음으로 pushStart로 설정해준다.
		calendar_id = calendar['calendar_id']
		calendar_channel_id = calendar['google_channel_id']
		if '@gmail.com' in calendar_id or '@naver.com' in calendar_id or '@ical.com' in calendar_id:
			calendarModel.updateGoogleSyncState(calendar_channel_id,GOOGLE_SYNC_STATE_PUSH_START)			

	# account = calendarModel.getHashkey(calendar['id'])

		


	#notification 저장하기.
	#기존 state가 ==0 이고 이 요청을 보낸상태면 1로 바꿘준다.
	#watch에서 받았으면 2로 값을바꾸고 push Notification을 보낸다.
	for idx, calendar in enumerate(calendars):
		
		logging.debug('calender id =>'+calendar['id'])		
		calendar_id = calendar['id']
		if '@gmail.com' in calendar_id or '@naver.com' in calendar_id or '@ical.com' in calendar_id:
			watch_URL = 'https://www.googleapis.com/calendar/v3/calendars/'+calendar['id']+'/events/watch'
			body = {
				"id" : arr_channel_id[idx],
				"type" : "web_hook",
				"address" : "https://ssoma.xyz:55566/v1.0/sync/watchReciver",
				"token" : sessionkey
			}						
			res = network_manager.reqPOST(watch_URL,access_token,body)
			#start push noti
			
		# if 'id' in res:
		# 	calendarModel.updatePushComplete(arr_channel_id[idx],CALENDAR_PUSH_STATE_BEFORE)

			logging.info('ress=s==> '+str(res))
		#codeReview
		#status code 를 202등으로 바꾼다.
	return utils.syncState(SYNC_GOOGLE_SUCCES,None)

def reqEventsList(sessionkey,calendar,user,body={}):

	channel_id = calendar['google_channel_id']
	account_hashkey = calendar['account_hashkey']
	access_token = user[0]['access_token']
	calendar_hashkey = calendar['calendar_hashkey']
	calendar_id = calendar['calendar_id']

	URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events?'
	
	res = json.loads(network_manager.reqGET(URL,access_token,body))


	for item in res['items']:
		
		# logging.debug('event_id=>'+str(item['id']))

		event_id = item['id']		
		summary = 'noTitle'
		start_date = None
		end_date = None
		created = None
		updated = None
		location = 'noLocation'

		if('summary' in item):			
			summary = item['summary']
		if('location' in item):
			location = item['location']

		if('date' in item['start'] ):					
			start_date = item['start']['date']
			end_date = item['end']['date']

		elif('dateTime' in item['start']):		
			start_date = utils.date_utc_to_current(str(item['start']['dateTime']))
			end_date = utils.date_utc_to_current(str(item['end']['dateTime']))
											
		created = str(item['created'])[:-1]
		updated = str(item['updated'])[:-1]
		event_hashkey = utils.makeHashKey(event_id)
		eventModel.setGoogleEvents(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location)



	#넥스트 토큰이있을경우 없을때까지 요청을 보낸다.
	if 'nextPageToken' in res:
		
		body = {
					'maxResults': 10,
					'pageToken' : str(res['nextPageToken'])
				}
		reqEventsList(sessionkey,calendar,user,body)

	else :
		
		

		syncToken = res['nextSyncToken']
		logging.debug('syncToken==>'+syncToken)

		#해당캘린더의 싱크가 끝낫다+> syncToken을 저장해둔다.
		syncModel.setSync(calendar_hashkey,syncToken)
		#캘린 더 해시키에 해당하는 googlePushComplete 1로만든다.
		calendarModel.updateGoogleSyncState(channel_id,GOOGLE_SYNC_STATE_EVENTS_END)
 

