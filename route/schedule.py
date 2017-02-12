from manager.redis import redis
from manager import network_manager
from flask.views import MethodView
import json
from manager import db_manager
import flask
import urllib
import uuid
from common.util import utils


class Schedule(MethodView):
	def get(self,action):
		if action == 'getCalendarList':
			calendarListURL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
			calendarList = json.loads(network_manager.reqGET(calendarListURL))
			print(calendarList)
			returnValue = {}
			dataArray = []
			data = {}

			# returnValue['userId'] = redis.get('session_key');

			for item in calendarList['items']:
				data = {}
				data['id'] = item['id']
				data['name'] = item['summary']
				dataArray.append(data)

			returnValue['data'] = dataArray

			return json.dumps(returnValue)

		elif action == 'setCalendarList':
			dataArray = flask.request.args.get('data')
			session_key = flask.request.args.get('session_key')	
			alreadySyncCnt = 0;

			arrAlready = []
			print(dataArray)			
			# calendarData = ""	
			# 	calendarData += "("+item['id']+","+userId+"),"
			# calendarData = calendarData[:-1]	
			try:
				for item in json.loads(dataArray):
					
					#FixME
					#uuid4가 랜덤하게 생성해주는것이므로 중복될경우가있을수있음.
					#md5등의 소트값이들어갈수있는 것으로 바꿔야됨.
					channelId = str(uuid.uuid4())
					print('channelid '+channelId)
									
					result = db_manager.query(
							"SELECT * FROM calendarList WHERE calendar_id = %s",([item['id']])
						)
					rows = utils.fetch_all_json(result)

					#길이가 0 이면 아예 등록되지않은상태.
					if len(rows) == 0: 
						db_manager.query(
									"INSERT INTO calendarList " 
									"(`calendar_id`, `session_key`,`channel_id`)"
									"VALUES"
									"(%s, %s, %s)",
									(			
										item['id'],session_key,channelId
									)
								)			
						URL = 'https://www.googleapis.com/calendar/v3/calendars/'+item['id']+'/events/watch'
						body = {
							"id" : channelId,
							"type" : "web_hook",
							"address" : "https://ssoma.xyz:55566/googleReceive"
						}						
						res = network_manager.reqPOST(URL,body)
						print('notification result =>'+res)
						if(res == 'Not Found'):
							print('Nope!')
							self.setEvents(channelId)
					else:
						alreadySyncCnt += 1				
						arrAlready.append(item['id'])
				
				# if alreadySyncCnt > 0:
				# 	print('item=>'+item['id'])
					
				if alreadySyncCnt>0 :
					redis.publish('syncAlert', 'already sync! => '+ str(arrAlready))		
		
			except Exception as e:
				print("erorr => "+str(e))

			return 'good'
		elif action == 'getEvents':
			session_key = flask.request.args.get('session_key')
			print(session_key)
			result = db_manager.query(
							"SELECT * FROM (user LEFT JOIN calendarList ON user.session_key = calendarList.session_key ) LEFT JOIN events ON calendarList.calendar_id = events.calendar_id WHERE user.session_key = %s",(session_key,)
						)
			rows = utils.fetch_all_json(result)
			print(rows)
			return json.dumps(rows)

	def setEvents(self,channel_id):
		# mail = flask.request.args.get('mail')		
		# print('setAlleventsCall')
		result = db_manager.query(
				"SELECT * FROM calendarList WHERE channel_id = %s",(channel_id,)
			)
		rows = utils.fetch_all_json(result)
		
		for row in rows:	
			URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(str(row['calendar_id']))+'/events'
			print('url =>'+URL)
			res = json.loads(network_manager.reqGET(URL))
			# print('calender_id=>'+row['calendar_id'])
			# print('ressss=>'+str(res))
			# print('res=> ' + str(res['summary']))		
			calendar_id = row['calendar_id']
			syncToken = res['nextSyncToken']

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
			#해당 syncToken을 업데이트해준다.
			print('sync==>'+syncToken)
			db_manager.query(
				"INSERT INTO sync " 
				"(calendar_id,sync_token,ctime) "
				"VALUES "
				"(%s, %s, now()) ",
				(			
					calendar_id,syncToken
				)
			)		
	
			

