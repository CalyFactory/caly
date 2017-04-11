
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
from model import googleWatchInfoModel

from common import caldavWrapper
from common import gAPI
from manager import network_manager

import json
import urllib
from manager.redis import redis
from common.util.statics import *

import sync_worker
from common import statee
from bot import slackAlarmBot
import json 

#time
from datetime import timedelta,datetime
from pytz import timezone
import time


with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

#caldav 동기화요청로직.
#user는 유저계정
#apikey는 유저 접근 토큰키
#login_platform은 로그인 플랫폼(ical/naver)
#time_state 과거/미래를 알려주는 flag
def caldav(user,apikey,login_platform,time_state):
	
	#forward일경우 미래 일정 싱크시작
	log_state = time_state == SYNC_TIME_STATE_FORWARD and LIFE_STATE_CALDAV_FORWARD_SYNCING or LIFE_STATE_CALDAV_BACKWARD_SYNCING
	statee.userLife(apikey,log_state)

	
	state = time_state == SYNC_TIME_STATE_FORWARD and SYNC_END_TIME_STATE_FORWARD or SYNC_END_TIME_STATE_BACKWARD
	syncEndRows = syncEndModel.getSyncEnd(user[0]['account_hashkey'],state)

	#한번이라도 동기화했나?
	#동기화이미됬다고 리턴
	if len(syncEndRows) != 0 :
		return utils.syncState(SYNC_CALDAV_ERR_ALREADY_REIGITER,MSG_SYNC_ALREADY)
	
	

	u_id = user[0]['user_id']
	u_pw = user[0]['access_token']
	account_hashkey = user[0]['account_hashkey']			
	
	#캘데브 로그인
	calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)

	principal = calDavclient.getPrincipal()
	homeset = principal.getHomeSet()
	calendars = homeset.getCalendars()
		
	for idx,calendar in enumerate(calendars):
		#outbox인경우 403에러가 발생함으로 이것은  빼버린다
		if  '/calendars/outbox/' in calendar.calendarUrl and login_platform == 'ical':
			calendars.pop(idx)		
		#calendarid가 calendars인경우 이것도 뺀다.
		#모든캘린더를 모아둔 데이터로 중복으로 이벤트가 저장되게된다.
		if calendar.calendarId == 'calendars':
			calendars.pop(idx)

	#캘린더 해시키를 먼저 만든다.
	arr_calendar_hashkey = []


	

	#최초 forward로 돌때는 캘린더에 해시키를 저장해줘야된다.
	#아닐경우는 그냥 기존것에 더해주면된다.	
	if time_state == SYNC_TIME_STATE_FORWARD:
		for idx,calendar in enumerate(calendars):
			logging.info('calenndarrr'+str(calendar.calendarUrl))

			# 캘린더url + login_platform이 같으면 항상 같은 값이나오도록한다.
			# 이는 후에 background에서 돌경우 같은 캘린더를 찾긱위해 디비를 다시 돌지 않게 하기 위함이다		
			calendar_hashkey = utils.makeHashKey(calendar.calendarUrl+login_platform)
			arr_calendar_hashkey.append(calendar_hashkey)

		logging.info('SYNC FORWARD')
		try:
			calendarModel.setCaldavCalendar(calendars,account_hashkey,arr_calendar_hashkey)
		except Exception as e:
			logging.error(str(e))
			return utils.syncState(SYNC_CALDAV_ERR_SET_CALENDAR,str(e))
	
	#backward일경우 기존 디비 뒤져서 hashkey를 넣어준다.
	elif time_state == SYNC_TIME_STATE_BACKWARD:
		calendarsInDB = calendarModel.getAllCalendarWithAccountHashkey(account_hashkey)	

	##TODO
	##RANGE를 현재시간부터 5개월후로!
	if time_state == SYNC_TIME_STATE_FORWARD:

		range_start = time.strftime("%Y%m%dT000000Z")
		range_end = datetime.now()+ timedelta(hours=MONTH_TO_HOUR * 5)
		range_end = datetime.strftime(range_end, "%Y%m%dT000000Z") 	

	##RANGE를 현재시간으로부터 과거 3년치
	elif time_state == SYNC_TIME_STATE_BACKWARD:
		range_end = time.strftime("%Y%m%dT000000Z")
		range_start = datetime.now() - timedelta(hours=YEAR_TO_HOUR * 3)
		range_start = datetime.strftime(range_start, "%Y%m%dT000000Z") 							

		logging.info('range_start ==> '+range_start)
		logging.info('range_edn ==> '+range_end)	

	#캘린더 안에있는 이벤트들을 예쁘게 발라서 디비에 저장한다.
	for idx,calendar in enumerate(calendars):

			
		logging.info('calnedarsss=> ' + calendar.calendarName)
		logging.info('url => ' + calendar.calendarUrl)


		#언제부터 언제까지 일정을 가져올지를 정한다.
		eventList = calendar.getEventByRange( range_start, range_end)					
		eventDataList = calendar.getCalendarData(eventList)

		
		if time_state == SYNC_TIME_STATE_FORWARD:
			calendar_hashkey = arr_calendar_hashkey[idx]
			
		elif time_state == SYNC_TIME_STATE_BACKWARD:
			for calendarDB in calendarsInDB:
				if calendar.calendarUrl == calendarDB['caldav_calendar_url']:
					calendar_hashkey = calendarDB['calendar_hashkey']
		


		logging.info('eventDataList==>'+str(eventDataList))
		for event_set in eventDataList:		
			logging.info('eventsetttt => ' + str(event_set.eventData))
			event = event_set.eventData['VEVENT']	
			logging.info('난 바꿨는데?')	
			#네이버일경우만!		
		   	#만약 Transparet인 이벤트라면 다음 루프로 넘어간다.
		   	#ical일경우는 타면안된다.
			# if 'TRANSP' in event:
			# 	if event['TRANSP'] == 'TRANSPARENT' and login_platform == 'naver':
			# 		continue
			# 	elif login_platform == 'ical':
			# 		pass

			# #uid를 eventId로 쓰면된다.
			event_id = event_set.eventId
			event_hashkey = utils.makeHashKey(event_id)
			caldav_event_url = event_set.eventUrl
			caldav_etag = event_set.eTag
			summary = None
			location = None
			start_dt = None
			end_dt = None
			created_dt = None
			updated_dt = None
			#반복 설정.
			recurrence = None


			#키값이 없는경우가 있어아 아래와같이 예외처리가들어가야한다.
			if 'SUMMARY' in event:
				summary = event['SUMMARY']			

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
			if 'CREATED' in event:
				created_dt = event['CREATED']
				if(isinstance(created_dt,datetime)):
					created_dt =created_dt.astimezone(timezone('Asia/Seoul'))					  			
			#문자열을 날짜시간으로 변경해줌. 

			if 'LAST-MODIFIED' in event:
				updated_dt = event['LAST-MODIFIED']
	
			if(isinstance(updated_dt,datetime)):
					#한국시간으로바꿔준다
				updated_dt =updated_dt.astimezone(timezone('Asia/Seoul'))					  							
				
			else:		
				updated_dt = created_dt

			if 'LOCATION' in event:	
				if event['LOCATION'] == '':
					location = None
				else:
					location = event['LOCATION']

			if 'RRULE' in event:
				recurrence = event['RRULE']
				startIndex = recurrence.index("{")
				endIndex = recurrence.index("}")
				recurrence = recurrence[startIndex+1:endIndex]

			logging.info('hashkey=>' + calendar_hashkey)	
			logging.info('event_hashkey=>' + event_hashkey)	
			logging.info('event_id=>' + event_id)	
			logging.info('caldav_event_url=>' + caldav_event_url)	
			logging.info('caldav_etag=>' + caldav_etag)	
			logging.info('summary=>' + summary)
			logging.info('start_dt=>' + str(start_dt))
			logging.info('end_dt=>' + str(end_dt))
			logging.info('created_dt=>' + str(created_dt))
			logging.info('updated_dt=>' + str(updated_dt))
			logging.info('location=>' + str(location))
			
			try:
				#이벤트를 저장한다.
				eventModel.setCaldavEvents(event_hashkey,calendar_hashkey,event_id,summary,start_dt,end_dt,created_dt,updated_dt,location,caldav_event_url,caldav_etag,recurrence)
			except Exception as e:
				logging.error(str(e))
				return utils.syncState(SYNC_CALDAV_ERR_SET_EVENTS,str(e))

		
		try:
			#캘린더마다 싱크된 타임을 기록해준다. 
			syncModel.setSync(calendar_hashkey,'null')
		except Exception as e:
			logging.error(str(e))
			return utils.syncState(SYNC_CALDAV_ERR_SET_SYNC_TIME,str(e))

	try:
		#싱크 끝난상황을 저장해둔다.
		state = time_state == SYNC_TIME_STATE_FORWARD and SYNC_END_TIME_STATE_FORWARD or SYNC_END_TIME_STATE_BACKWARD
		syncEndModel.setSyncEnd(account_hashkey,state)
			
	except Exception as e:
		logging.error(str(e))
		return utils.syncState(SYNC_CALDAV_ERR_SET_SYNC_END,str(e))

	log_state = time_state == SYNC_TIME_STATE_FORWARD and LIFE_STATE_CALDAV_FORWARD_SYNC_END or LIFE_STATE_CALDAV_BACKWARD_SYNC_END
	statee.userLife(apikey,log_state)	
	# 미래것이 끝났고 에러없이 마무리됬다면, 과거꺼를 돌려야한다. 
	# 미래것일 상태에서만 요청을 하도록 한다.	
	if time_state == SYNC_TIME_STATE_FORWARD:
		slackAlarmBot.alertSyncEnd()
		data = {}
		data['user'] = user
		data['user_hashkey'] = user[0]['user_hashkey']
		data['login_platform'] = login_platform
		data['apikey'] = apikey
		#워커에게 작업을 요청한다.
		sync_worker.worker.delay(data)		

	return utils.syncState(SYNC_CALDAV_SUCCESS,None)


#구글 동기화 요청로직
#user 는 유저계정
#apikey는 유저토큰
#time_state 과거/미래를 알려주는 flag
def google(user,apikey,time_state):	
	
	log_state = time_state == SYNC_TIME_STATE_FORWARD and LIFE_STATE_GOOGLE_FORWARD_SYNCING or LIFE_STATE_GOOGLE_BACKWARD_SYNCING
	statee.userLife(apikey,log_state)

	#걸리는 시간 체크
	utils.checkTime(datetime.now(),'start')
	
	state = time_state == SYNC_TIME_STATE_FORWARD and SYNC_END_TIME_STATE_FORWARD or SYNC_END_TIME_STATE_BACKWARD
	syncEndRows = syncEndModel.getSyncEnd(user[0]['account_hashkey'],state)

	#한번이라도 동기화했나?
	if len(syncEndRows) != 0 :
		return utils.syncState(SYNC_CALDAV_ERR_ALREADY_REIGITER,MSG_SYNC_ALREADY)
	

	access_token = user[0]['access_token']
	account_hashkey = user[0]['account_hashkey']
	
	#calendarList를 가져오기위한 Google api요
	calendar_list_URL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
	calendar_list = json.loads(network_manager.reqGET(calendar_list_URL,access_token))
	
	logging.info('calendarList=>' + str(calendar_list)	)
	
	calendars = calendar_list['items']


	#디비에 channel_id를 array로 다이렉트로 넣기위한 코드.
	arr_channel_id = []

	arr_calendar_hashkey = []

	for calendar in calendars:
		calendar_channelId = utils.makeHashKey(calendar['id'])		
		arr_channel_id.append(calendar_channelId)		

	if time_state == SYNC_TIME_STATE_FORWARD:			
		try:
			#최초 googlepushcomplete 가 0
			calendarModel.setGoogleCalendar(calendars,account_hashkey,arr_channel_id)
		except Exception as e:
			logging.error(str(e))
			return utils.syncState(SYNC_GOOGLE_ERR_SET_CALENDAR,str(e))		

	calendarsInDB = calendarModel.getAllCalendarWithAccountHashkey(account_hashkey)



	#TODO
	#maxResults가 최대 몇개까지인지 확인하고 최대로 가져온다.
	#RANGE를 현재시간부터 5개월후로!
	if time_state == SYNC_TIME_STATE_FORWARD:

		range_start = time.strftime("%Y-%m-%dT00:00:00-09:00")
		range_end = datetime.now() + timedelta(hours = MONTH_TO_HOUR * 5)
		range_end = datetime.strftime(range_end, "%Y-%m-%dT00:00:00-09:00")

	
	elif time_state == SYNC_TIME_STATE_BACKWARD:

		range_end = time.strftime("%Y-%m-%dT00:00:00-09:00")
		range_start = datetime.now() - timedelta(hours = YEAR_TO_HOUR * 3)
		range_start = datetime.strftime(range_start, "%Y-%m-%dT00:00:00-09:00")	

	logging.info('range_start ==> '+range_start)
	logging.info('range_edn ==> '+range_end)

	#timeMin,Max로 언제까지의 데이터를 가져올건지정한다.
	for calendar in calendarsInDB:
		logging.info('[timeTest]calendar ForLoop==> '+str(utils.checkTime(datetime.now(),'ing')))
		body = {
					'maxResults': 1000,
					'timeMin':range_start,
					'timeMax':range_end					
				}	
		reqEventsList(time_state,apikey,calendar,user,body)

		#캘린더 id가 일반계정이면==>무조건 push를 받음으로 pushStart로 설정해준다.
		calendar_id = calendar['calendar_id']
		calendar_channel_id = calendar['google_channel_id']
		if '@gmail.com' in calendar_id or '@naver.com' in calendar_id or '@ical.com' in calendar_id or '@group.calendar.google.com' in calendar_id:
			if time_state == SYNC_TIME_STATE_FORWARD:
				calendarModel.updateGoogleSyncState(calendar_channel_id,GOOGLE_SYNC_STATE_PUSH_START)			

	logging.info('[timeTest]end All event Save==> '+str(utils.checkTime(datetime.now(),'ing')))			
	#notification 저장하기.
	#기존 state가 ==0 이고 이 요청을 보낸상태면 1로 바꿘준다.
	#watch에서 받았으면 2로 값을바꾸고 push Notification을 보낸다.
	#모든캘린더에대해서 처음에만 진행한다(미래)
	if time_state == SYNC_TIME_STATE_FORWARD:
		#10년동한 우린 알람을 받고자한다.
		logging.info('his')
		# logging.info( datetime.now())
		expp = datetime.now()+ timedelta(hours=MONTH_TO_HOUR)
		# exp = datetime.utcnow() + timedelta(hours = 9 )
		logging.info('exp =>'+str(expp))
		logging.info('exp =>'+str(expp.timestamp()))
		exp_unix_time = int(expp.timestamp()*1000) 
		
		logging.info('google expiration -> '+str(exp_unix_time))
				
		for idx, calendar in enumerate(calendars):
			logging.info('[timeTest]watch Request==> '+str(utils.checkTime(datetime.now(),'ing')))			
			logging.info('calender id =>'+calendar['id'])		
			calendar_id = calendar['id']

			#안되는 캘린더가의 경우가 존재함으로 현재 검증된것들만 동기화되도록한다.
			if '@gmail.com' in calendar_id or '@naver.com' in calendar_id or '@ical.com' in calendar_id or '@group.calendar.google.com' in calendar_id:
				#변경된 정보를 받기위한 push Notification api를 붙이는 과정이다.
				#캘린더고유값인 channelId와 콜백받을 address를 정해준다.
				# watch_URL = 'https://www.googleapis.com/calendar/v3/calendars/'+calendar['id']+'/events/watch'
				# body = {
				# 	"id" : arr_channel_id[idx],
				# 	"type" : "web_hook",
				# 	"address" : conf['googleWatchAddress'],
				# 	"token" : apikey,
				# 	"expiration" : str(exp_unix_time)+'000'
				# }						
				# res = json.loads(network_manager.reqPOST(watch_URL,access_token,body))

				#start push noti
				res = gAPI.attachWatch(calendar['id'],arr_channel_id[idx],apikey,str(exp_unix_time)+'000',access_token)
				logging.info('watch res =>'+str(res))
				try:
					logging.info('giood') 
					logging.info(res['id']) 
					logging.info(expp) 
					logging.info(res['resourceId']) 

					calendarModel.updateGoogleExpiration(res['id'],expp,res['resourceId'])					
				except Exception as e:
					logging.error(str(e)) 
					
				googleWatchInfoModel.setGoogleWatchInfo(arr_channel_id[idx],GOOGLE_WATCH_CALL)
				# resource_id = res['resourceId']
				# arr_channel_id[] exp,resource_id
		
		#for loop가  다끝나면 나머지 과거 이벤트들을 받아야한다.
		#싱크가 끝났다는것을 슬랙봇으로 알려주고
		#워커가 과거일정을 실행하도록한다
		slackAlarmBot.alertSyncEnd()
		data = {}
		data['user'] = user
		data['login_platform'] = 'google'
		data['apikey'] = apikey
		sync_worker.worker.delay(data)	

	state = time_state == SYNC_TIME_STATE_FORWARD and SYNC_END_TIME_STATE_FORWARD or SYNC_END_TIME_STATE_BACKWARD
	syncEndModel.setSyncEnd(account_hashkey,state)					 

	log_state = time_state == SYNC_TIME_STATE_FORWARD and LIFE_STATE_GOOGLE_FORWARD_SYNC_END or LIFE_STATE_GOOGLE_BACKWARD_SYNC_END
	statee.userLife(apikey,log_state)	

	return utils.syncState(SYNC_GOOGLE_SUCCES,None)

#구글 이벤트리스트 요청 함
def reqEventsList(time_state,apikey,calendar,user,body={}):

	channel_id = calendar['google_channel_id']
	account_hashkey = calendar['account_hashkey']
	access_token = user[0]['access_token']
	calendar_hashkey = calendar['calendar_hashkey']
	calendar_id = calendar['calendar_id']

	#실제 캘린더아이디로 이벤트리스트를 요청한다.
	URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events?'
	
	res = json.loads(network_manager.reqGET(URL,access_token,body))

	logging.info('calendarResponse'+str(res))
	#받아온 아이템들을 예쁘게 발라서 디비에 저장한다.
	for item in res['items']:
		
		event_id = item['id']		
		summary = 'noTitle'
		start_date = None
		end_date = None
		created = None
		updated = None
		location = None
		recurrence = None

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

		if 'recurrence' in item:
			logging.info('rec => '+str(item['recurrence'][0]))			
			recurrence = item['recurrence'][0]

		event_hashkey = utils.makeHashKey(event_id)
		eventModel.setGoogleEvents(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location,recurrence)
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
		reqEventsList(time_state,apikey,calendar,user,body)

	else :
		
		

		syncToken = res['nextSyncToken']
		logging.info('syncToken==>'+syncToken)

		#해당캘린더의 싱크가 끝낫다+> syncToken을 저장해둔다.
		syncModel.setSync(calendar_hashkey,syncToken)
		if time_state == SYNC_TIME_STATE_FORWARD:
		#캘린 더 해시키에 해당하는 googlePushComplete 1로만든다.
			calendarModel.updateGoogleSyncState(channel_id,GOOGLE_SYNC_STATE_EVENTS_END)
 

