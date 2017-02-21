#-*- coding: utf-8 -*-
# author : yenos
# describe : sync로직을 담당하는 api이다.

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



class Sync(MethodView):
#sync는 캘린더 리스트 가져오기 => 이벤트리스트 저장하기.(최신기록 먼저)

	def post(self,action):
		if action == 'sync':

			sessionkey = flask.request.form['sessionkey']
			#세션키에대한 해시키를 가져온다.
			user_hashkey = redis.get(sessionkey)

			logging.debug('sessionkey = >'+str(sessionkey))
			logging.debug('hashkey = >'+str(user_hashkey))
			

			user = userAccountModel.getUserAccount(user_hashkey)
			
			login_platform = user[0]['login_platform']

			if login_platform == 'naver' or login_platform == 'ical':
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
				    return utils.resErr(str(e))	
				
				logging.debug('hashkey = >' + str(arr_calendar_hashkey))

				for idx,calendar in enumerate(calendars):
				    
				    logging.debug('calnedarsss=> ' + calendar.calendarName)

				    eventList = calendar.getEventByRange( "20170128T000000Z", "20180223T000000Z")				    
				    eventDataList = calendar.getCalendarData(eventList)
				    calendar_hashkey = arr_calendar_hashkey[idx]
					# print('eventDataList = >'+ str(eventDataList))
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
				  
					    #coderReview
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
						    return utils.resErr(str(e))

					#캘린더마다 싱크된 타임을 기록해준다. 
				    try:
					    syncModel.setSync(calendar_hashkey,'null')
				    except Exception as e:
					    return utils.resErr(str(e))

				try:
					syncEndModel.setSyncEnd(account_hashkey)
				except Exception as e:
					return utils.resErr(str(e))				


				return utils.resSuccess({'msg':'Caldav Sync Success'})

			elif login_platform == 'google':
				access_token = user[0]['access_token']
				account_hashkey = user[0]['account_hashkey']

				calendar_list_URL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
				calendar_list = json.loads(network_manager.reqGET(calendar_list_URL,access_token))
				
				logging.debug('calendarList=>' + str(calendar_list)	)
				
				calendars = calendar_list['items']

				arr_channel_id = []
				for calendar in calendars:
					calendar_channelId = utils.makeHashKey(calendar['id'])
					arr_channel_id.append(calendar_channelId)
						
				logging.debug('channl=> ' + str(arr_channel_id))	

				calendarModel.setGoogleCalendar(calendars,account_hashkey,arr_channel_id)

				#notification 저장.
				for idx, calendar in enumerate(calendars):
					
					logging.debug('calender id =>'+calendar['id'])
					watch_URL = 'https://www.googleapis.com/calendar/v3/calendars/'+calendar['id']+'/events/watch'
					body = {
						"id" : arr_channel_id[idx],
						"type" : "web_hook",
						"address" : "https://ssoma.xyz:55566/v1.0/sync/watchReciver"
					}						
					res = network_manager.reqPOST(watch_URL,access_token,body)
					#codeReview
					#status code 를 202등으로 바꾼다.
				return utils.resSuccess({'msg':'Google Sync Loading'})

	#watchReciver를 테스트해봐야됨.
		elif action == 'watchReciver':
			
			logging.info('watch')
			logging.info(str(flask.request.headers))				

			channelId = flask.request.headers['X-Goog-Channel-Id']
			state = flask.request.headers['X-Goog-Resource-State']

			account = calendarModel.getHashkey(channelId)
			#해당채널아이다로 가지고있는 것을 찾고
			rows = calendarModel.getCalendar(channelId)
			logging.debug('calender id =>' + str(rows))
			#pushtoken으로부터 acocunt_hashkey를 가지는 모든 googe_pushComplete를 확인핸다.
			#모두 다 1이되어있으면 완료되었음을 푸시로보낸다.


			if len(rows) != 0:
			#해당 푸시컴프리트 값을 1로 바꿔준다.(푸시가 잘왔으니까.)
			
				if len(rows) != 0 and rows[0]['google_push_complete'] == 0 and state == 'sync':
					calendarModel.updatePushComplete(channelId)
					# event를세팅해준다.

					for row in rows:	
						#최초 요청은 nextPageToken이 존재하지 않는다.
						body = {
									'maxResults': 10
								}
						calendar_hashkey = str(row['calendar_hashkey']);
						calendar_id = str(row['calendar_id']);
						print(calendar_id)
						#event로직이 성공적으로 끝낫을경우. 						
						self.reqEventsList(channelId,account[0]['account_hashkey'],account[0]['access_token'],calendar_hashkey,calendar_id,body)
							 
						
				else:
					
					calendar_hashkey = str(rows[0]['calendar_hashkey'])
					calendar_id = str(rows[0]['calendar_id'])
					
					#해당 캘린더의 최근의 sync토큰을 가져온다.
					row = calendarModel.getLatestSyncToken(calendar_hashkey)
					
					sync_token = row[0]['sync_token'];
					calendar_hashkey = row[0]['calendar_hashkey'];
					calendar_id = row[0]['calendar_id'];

					logging.debug('synctoken =>' + sync_token)
					logging.debug('calendar_id = >'+calendar_id)
					
					
					URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events'
					body = {
						'syncToken':sync_token
					}
					res = json.loads(network_manager.reqGET(URL,account[0]['access_token'],body))				
					logging.debug('nextPage' + str(res))

					next_sync_token = res['nextSyncToken']								
					syncModel.setSync(calendar_hashkey,next_sync_token)			

					#기본적으로 아이템에 값이 있어야한다.
					if len(res['items']) != 0:					

						for item in res['items']:
							
							# add/update/delete 모든 공통적인부분 id를 가진다.
							event_id = item['id']
							status = item['status']
							location = 'noLocation'
							if('location' in item):
								location = item['location']													

							#삭제는 아래와같은 키값들을 제공해주지 않는다.
							if status != 'cancelled':
							#confirmed, canceled							
								created = item['created']
								updated = item['updated']

								
								created = created[:len(created)-5]
								updated = updated[:len(updated)-5]	
								summary = 'noTitle'
								if('summary' in item):												
									summary = item['summary']
								logging.debug('created => '+ created)
								logging.debug('updated => '+ updated)
								logging.debug('status => ' + status)									
								
							
							# 만들어진 경우 or 수정일 경우이다.
							# created 와 updated가 같은경우 추가한경우다
							# 아예 instrt해주면된다.
								if('date' in item['start'] ):					
									start_date = item['start']['date']
									end_date = item['end']['date']

								elif('dateTime' in item['start']):		
									start_date = utils.date_utc_to_current(str(item['start']['dateTime']))
									end_date = utils.date_utc_to_current(str(item['end']['dateTime']))					

							if status == 'confirmed' and created == updated:
								logging.debug('addEvent')
								event_hashkey = utils.makeHashKey(event_id)

								eventModel.setGoogleEvents(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location)
					
							#업데이트 한 경우이다. 
							#id값을 찾아서 변환된값을 바꿔준다.
							elif status =='confirmed' and created != updated:
								logging.debug('updated')
								# update events set calendar_id = 'testid', summary = 'sum' where id = '67'
								eventModel.updateEvents(summary,start_date,end_date,created,updated,location,event_id)
							

							elif status == 'cancelled':
								logging.debug('cancelled')							
								eventModel.deleteEvents(event_id)
			elif len(rows)==0:
				#이벤트가없을경우 원래 이벤틀르 가져올수없는경우다. 동기화한샘친다.
				logging.debug('no Event')
				calendarModel.updateEventEnd(channelId)					
						
			return 'hi'

	def reqEventsList(self,channelId,account_hashkey,access_token,calendar_hashkey,calendar_id,body={}):

		URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events?'
		
		res = json.loads(network_manager.reqGET(URL,access_token,body))
		# print('calender_id=>'+row['calendar_id'])
		
		logging.debug('ress=>'+str(res))
	

		for item in res['items']:
			
			logging.debug('event_id=>'+str(item['id']))

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
			self.reqEventsList(channelId,account_hashkey,access_token,calendar_hashkey,calendar_id,body)

		else :
			
			logging.debug('sync==>'+res['nextSyncToken'])

			syncToken = res['nextSyncToken']
			syncModel.setSync(calendar_hashkey,syncToken)

			calendarModel.updateEventEnd(channelId)
			completeCalendars = calendarModel.getGooglePushComplete(account_hashkey)
			
			logging.debug('calendarSync =>'+str(CALENDAR_SYNC))
			logging.debug('calendarSync =>'+str(completeCalendars))
			
			is_finished_sync = True
			for completeCalendar in completeCalendars:
				if completeCalendar['google_push_complete'] != CALENDAR_SYNC:
					is_finished_sync = False

			#다 정상적으로 끝냇으면
			if is_finished_sync:
				
				logging.info('sync success')
				#모든캘린더들이 다 싱크가 완료되었다면 syncEnd에 값을 저장한다.  
				try:
					syncEndModel.setSyncEnd(account_hashkey)
				except Exception as e:
						return utils.resErr(str(e))

				push_token = userDeviceModel.getPushToken(account_hashkey)[0]['push_token']
				
				logging.debug('pushtoken =>' + push_token)
				data_message = {
				    "type" : "sync",
				    "action" : "actions"
				}
				
				FCM.sendOnlyData(push_token,data_message)				

			else:
				logging.info('sync fail')
