#-*- coding: utf-8 -*-
# author : yenos
# describe : sync로직을 담당하는 api이다.

from flask.views import MethodView
import flask
from manager.redis import redis
from flask import session
from common.util import utils

from model import userDeviceModel
from model import userAccountModel
from model import userModel
from model import calendarModel
from model import eventModel
from model import syncModel

from common import caldavWrapper
from common import gAPI
from manager import network_manager
from manager import db_manager
import json
import urllib


class Sync(MethodView):
#sync는 캘린더 리스트 가져오기 => 이벤트리스트 저장하기.(최신기록 먼저)

	def post(self,action):
		if action == 'sync':
			# session['key'] = '123'

			sessionkey = flask.request.form['sessionkey']
			#세션키에대한 해시키를 가져온다.
			user_hashkey = session[sessionkey]
			print('hashekuy = >'+session[sessionkey])

			user = userAccountModel.getUserAccount(user_hashkey)
			print('user'+str(user))
			login_platform = user[0]['login_platform']
			if login_platform == 'naver' or login_platform == 'ical':
				u_id = user[0]['user_id']
				u_pw = user[0]['access_token']
				account_hashkey = user[0]['account_hashkey']			
				calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)
				calendarModel.setCaldavCalendar(calDavclient.getPrincipal().getHomeSet().getCalendars(),account_hashkey)
			
			elif login_platform == 'google':
				access_token = user[0]['access_token']
				account_hashkey = user[0]['account_hashkey']
				calendar_list_URL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
				calendar_list = json.loads(network_manager.reqGET(calendar_list_URL,access_token))
				print(calendar_list)
				calendars = calendar_list['items']

				arr_channel_id = []
				for calendar in calendars:
					calendar_channelId = utils.makeHashKey(calendar['id'])
					arr_channel_id.append(calendar_channelId)

				print('ca;=> '+ str(calendars))		
				print('channl=> '+str(arr_channel_id))		
				calendarModel.setGoogleCalendar(calendars,account_hashkey,arr_channel_id)

				#notification 저장.
				for idx, calendar in enumerate(calendars):
					print('calender id =>'+calendar['id'])
					watch_URL = 'https://www.googleapis.com/calendar/v3/calendars/'+calendar['id']+'/events/watch'
					body = {
						"id" : arr_channel_id[idx],
						"type" : "web_hook",
						"address" : "https://ssoma.xyz:55566/v1.0/sync/watchReciver"
					}						
					res = network_manager.reqPOST(watch_URL,access_token,body)

				return 'hi'

	#watchReciver를 테스트해봐야됨.ㅇㅇ
		elif action == 'watchReciver':
			print('watche call')
			print('headr=> '+str(flask.request.headers))
			print('cid=> '+str(flask.request.headers['X-Goog-Channel-Id']))
			channelId = flask.request.headers['X-Goog-Channel-Id']
			state = flask.request.headers['X-Goog-Resource-State']

			account = calendarModel.getHashkey(channelId)
			#해당채널아이다로 가지고있는 것을 찾고
			rows = calendarModel.getCalendar(channelId)
			print(rows)

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
						self.reqEventsList(account[0]['access_token'],calendar_hashkey,calendar_id,body)				
				else:
					
					calendar_hashkey = str(rows[0]['calendar_hashkey'])
					calendar_id = str(rows[0]['calendar_id'])
					print('call change!')
					#가장 최근의 sync토큰을 가져온다.
					row = calendarModel.getLatestSyncToken(calendar_hashkey)
					
					sync_token = row[0]['sync_token'];
					calendar_hashkey = row[0]['calendar_hashkey'];
					calendar_id = row[0]['calendar_id'];

					print('synctoke = >'+sync_token)
					print('calendar_id = >'+calendar_id)				

					
					URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events'
					body = {
						'syncToken':sync_token
					}
					res = json.loads(network_manager.reqGET(URL,account[0]['access_token'],body))				
					print(res)
					print(res['items'])

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
								print('created => '+ created)
								print('updated => '+ updated)
								created = created[:len(created)-5]
								updated = updated[:len(updated)-5]	
								summary = 'noTitle'
								if('summary' in item):												
									summary = item['summary']
								print('created => '+ created)
								print('updated => '+ updated)
								print('status => '+ status)
							
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
								print('add events')
								event_hashkey = utils.makeHashKey(event_id)

								eventModel.setEvents(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location)
					
							#업데이트 한 경우이다. 
							#id값을 찾아서 변환된값을 바꿔준다.
							elif status =='confirmed' and created != updated:
								print("updated!!")
								# update events set calendar_id = 'testid', summary = 'sum' where id = '67'
								eventModel.updateEvents(summary,start_date,end_date,created,updated,location,event_id)
							

							elif status == 'cancelled':
								print('cancelled!')							
								eventModel.deleteEvents(event_id)
								
						
			return 'hi'

	def reqEventsList(self,access_token,calendar_hashkey,calendar_id,body={}):

		URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events?'
		
		res = json.loads(network_manager.reqGET(URL,access_token,body))
		# print('calender_id=>'+row['calendar_id'])
		print('ressss=>'+str(res))
	

		for item in res['items']:
			print('event_id=>'+str(item['id']))
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
			eventModel.setEvents(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location)



		#넥스트 토큰이있을경우 없을때까지 요청을 보낸다.
		if 'nextPageToken' in res:
			
			body = {
						'maxResults': 10,
						'pageToken' : str(res['nextPageToken'])
					}
			self.reqEventsList(access_token,calendar_hashkey,calendar_id,body)
		else :
			print('sync==>'+res['nextSyncToken'])
			syncToken = res['nextSyncToken']
			syncModel.setSync(calendar_hashkey,syncToken)
		
