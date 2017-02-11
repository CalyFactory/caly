#-*- coding: utf-8 -*-
from flask.views import MethodView

import json
from flask import redirect, url_for
from googleapiclient import discovery
from oauth2client import client
from manager import db_manager
from manager import network_manager
from common.util import utils
from common.util import statics
import flask
import urllib
from manager.redis import redis
from flask import Flask,session
import hashlib

from time import time
from flask import render_template



class GoogleAuth(MethodView):
	def get(self,action):
		if action == 'index':
			return flask.redirect('/googleAuthCallBack')
		elif action == 'googleAuthCallBack':
			print('callback')
			
			flow = client.flow_from_clientsecrets(
				'./key/client_secret.json',
				scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.readonly',
				redirect_uri='https://ssoma.xyz:55566/googleAuthCallBack'
			)
			if 'key' in session:
				print('session alive!')
			#위코드는아래와같다
			#Google은 사용자 인증 및 동의를 처리한 후 인증 코드를 반환합니다. 
			#애플리케이션은 액세스 토큰을 받기 위해 client_id 및 client_secret과 함께 인증 코드를 사용하며, 이 인증 코드는 사용자를 대신하여 API 요청을 인증하는 데 사용될 수 있습니다. 이 단계에서 애플리케이션은 이전에 받은 토큰이 만료될 경우 애플리케이션이 새 액세스 토큰을 받을 수 있게 해주는 갱신 토큰을 요청할 수도 있습니다.
			if 'code' not in flask.request.args:
				#구글로부터 url을 요청한다.
				auth_uri = flow.step1_get_authorize_url()
				return flask.redirect(auth_uri)		
			else:
				#최초 로그인일 경우.
				auth_code = flask.request.args.get('code')				
				#유저정보를 받아온다.
				credentials = json.loads(flow.step2_exchange(auth_code).to_json())
				print(credentials)
				print(credentials['access_token'])
				print(credentials['id_token']['email'])

				# redis.set('access_token',credentials['access_token'])
				
				user_email = credentials['id_token']['email']
				user_access_token = credentials['access_token']
				redis.set('user_access_token',credentials['access_token'])
				current_time = str(int(time()))
				
				# print("userName+current =>"+user_email+current_time)
				
				# session['key'] = 'user_email'
				
				#TODO				
						
				#유저가 없다면.
				result = db_manager.query(
					"SELECT * FROM user WHERE mail = %s",(credentials['id_token']['email'],)
				)
				rows = utils.fetch_all_json(result)
				
				#조회결과 없다면!디비에 넣는다. 
				if len(rows) == 0:
					#디비없으면 최초 1회만 넣어준다.					
					user_hashkey = hashlib.md5(str(user_email+current_time+'u').encode('utf-8')).hexdigest()
					session_key = hashlib.md5(str(user_email+current_time+'s').encode('utf-8')).hexdigest()					

					redis.set(session_key,user_hashkey)

					db_manager.query(
						"INSERT INTO user " 
						"(mail, access_token,session_key,user_hashkey)"
						"VALUES"
						"(%s, %s, %s, %s)",
						(			
							user_email,
							user_access_token,
							session_key,
							user_hashkey
						)
					)

				return render_template('syncList.html', sessionKey=session_key)			
				# return flask.redirect('/calendarSync')
		# elif action == 'calendarSync':
		# 	return redirect('https://ssoma.xyz:55566/syncList.html')

	def post(self,action):			
		if action == 'googleReceive':
			print('headr=> '+str(flask.request.headers))
			print('cid'+str(flask.request.headers['X-Goog-Channel-Id']))
			channelId = flask.request.headers['X-Goog-Channel-Id']
			state = flask.request.headers['X-Goog-Resource-State']

			result = db_manager.query(
					"SELECT * FROM calendarList WHERE channel_id = %s",(channelId,)
				)
			rows = utils.fetch_all_json(result)
			
			#channelId 같은게 있다면 isRegitPush를 1로 만들어준다.
			#이것은 푸시등록이 완벽히 됬음을 의미한다.
			if len(rows) != 0 and rows[0]['isRegitPush'] == 0 and state == 'sync':
				result = db_manager.query(
					"UPDATE calendarList SET isRegitPush = 1 WHERE channel_id = %s"
					,(channelId,)
				)
				self.setEvents(rows[0]['channel_id'])
				redis.publish('syncAlert', 'sync Success')
			#외부로부터 수정이있어 푸시가온경우이다.
			#1. 채널 id를 가지는 sync Token을 검색한다
			#2. 해당토큰을 이용해 캘린더 이벤트 리스틀 조회한다.
			#2.5 각종처리
			#3. 바귄 싱크토큰을 추가해준다
			else:				
				print("else")
				result = db_manager.query(
					"select * from calendarList left join sync on sync.calendar_id = calendarList.calendar_id  where channel_id = %s order by sync.ctime desc limit 1"
					,(channelId,)
				)
				row = utils.fetch_all_json(result)
				
				sync_token = row[0]['sync_token'];
				calendar_id = row[0]['calendar_id'];


				print('synctoke = >'+sync_token)
				print('calendar_id = >'+calendar_id)
				URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events'
				body = {
					'syncToken':sync_token
				}
				res = json.loads(network_manager.reqGET(URL,body))
				print(res['items'])
				#token 을 업데이트해준다
				next_sync_token = res['nextSyncToken']				
				db_manager.query(
					"INSERT INTO sync " 
					"(calendar_id,sync_token,ctime) "
					"VALUES "
					"(%s, %s, now()) ",
					(			
						calendar_id,next_sync_token
					)
				)				
				
				#기본적으로 아이템에 값이 있어야한다.
				if len(res['items']) != 0:					

					for item in res['items']:
						
						# add/update/delete 모든 공통적인부분 id를 가진다.
						event_id = item['id']
						status = item['status']

						#삭제는 아래와같은 키값들을 제공해주지 않는다.
						if status != 'cancelled':
						#confirmed, canceled							
							created = item['created']
							updated = item['updated']					
							print('created => '+ created)
							print('updated => '+ updated)
							created = created[:len(created)-5]
							updated = updated[:len(updated)-5]						
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
							db_manager.query(
								"INSERT INTO events " 
								"(calendar_id,event_id,summary,start_date,end_date,created,updated) "
								"VALUES "
								"(%s, %s, %s, %s, %s, %s, %s) ",
								(			
									calendar_id,event_id,summary,start_date,end_date,created,updated
								)
							)
							redis.publish('fetchCalendar', '[fetch] add Schedule htmlLink: '+str(item['htmlLink']))
						 

						#업데이트 한 경우이다. 
						#id값을 찾아서 변환된값을 바꿔준다.
						elif status =='confirmed' and created != updated:
							print("updated!!")
							# update events set calendar_id = 'testid', summary = 'sum' where id = '67'
							db_manager.query(
								"UPDATE events set " 
								"calendar_id  = %s,"
								"summary = %s, "
								"start_date = %s, "
								"end_date = %s, "
								"created = %s, "
								"updated = %s "
								"where event_id = %s",
								(			
									calendar_id,summary,start_date,end_date,created,updated,event_id
								)
							)
							redis.publish('fetchCalendar', '[fetch] updated Schedule htmlLink: '+str(item['htmlLink']))

						elif status == 'cancelled':
							print('cancelled!')							
							db_manager.query(
								"DELETE from events " 								
								"where event_id = %s",
								(			
									event_id,
								)
							)
							redis.publish('fetchCalendar', '[fetch] remove Schedule')


						# delete from uncle where id = 'unclecho' 
			return 'nothing'

	def setEvents(self,channel_id):
		# mail = flask.request.args.get('mail')		
		# print('setAlleventsCall')
		result = db_manager.query(
				"SELECT * FROM calendarList WHERE channel_id = %s",(channel_id,)
			)
		rows = utils.fetch_all_json(result)
		
		for row in rows:	
			#최초 요청은 nextPageToken이 존재하지 않는다.
			body = {
						'maxResults': 10
					}
			calendar_id = str(row['calendar_id']);
			print(calendar_id)
			self.reqEventsList(calendar_id,body)	
			#해당 syncToken을 업데이트해주고. 끝낸다.
			

	def reqEventsList(self,calendar_id,body={}):

		URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events?'
		
		res = json.loads(network_manager.reqGET(URL,body))
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

			if('summary' in item):			
				summary = item['summary']

			if('date' in item['start'] ):					
				start_date = item['start']['date']
				end_date = item['end']['date']

			elif('dateTime' in item['start']):		
				start_date = utils.date_utc_to_current(str(item['start']['dateTime']))
				end_date = utils.date_utc_to_current(str(item['end']['dateTime']))
								
				
			created = str(item['created'])[:-1]
			updated = str(item['updated'])[:-1]

			db_manager.query(
				"INSERT INTO events " 
				"(calendar_id,event_id,summary,start_date,end_date,created,updated) "
				"VALUES "
				"(%s, %s, %s, %s, %s, %s, %s) ",
				(			
					calendar_id,event_id,summary,start_date,end_date,created,updated
				)
			)


		#넥스트 토큰이있을경우 없을때까지 요청을 보낸다.
		if 'nextPageToken' in res:
			
			body = {
						'maxResults': 10,
						'pageToken' : str(res['nextPageToken'])
					}
			self.reqEventsList(
							calendar_id,
							body							
						)
		else :
			print('sync==>'+res['nextSyncToken'])
			syncToken = res['nextSyncToken']
			db_manager.query(
				"INSERT INTO sync " 
				"(calendar_id,sync_token,ctime) "
				"VALUES "
				"(%s, %s, now()) ",
				(			
					calendar_id,syncToken
				)
			)			



