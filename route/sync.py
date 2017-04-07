#-*- coding: utf-8 -*-
# author : yenos
# describe : sync로직을 담당하는 api이다.

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
from model import recoModel
from model import googleWatchInfoModel


from common import caldavWrapper
from common import gAPI
from manager import network_manager

import json
import urllib
from datetime import timedelta,datetime
from common import FCM
from model import mFcmModel
from manager.redis import redis
from common.util.statics import *
from common import gAPI

# from model import userLifeModel
from common import statee
from common import syncLogic
from bot import slackAlarmBot

class Sync(MethodView):
#sync는 캘린더 리스트 가져오기 => 이벤트리스트 저장하기.(최신기록 먼저)

	def post(self,action):
		if action == 'sync':

			apikey = flask.request.form['apikey']
			user_hashkey = redis.get(apikey)
			
			if not user_hashkey:			
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)			
			#세션키에대한 해시키를 가져온다.
			logging.debug('apikey = >'+str(apikey))
			logging.debug('hashkey = >'+str(user_hashkey))
			

			user = userAccountModel.getUserAccount(user_hashkey)
			
			login_platform = user[0]['login_platform']

			#user_state
		

			if login_platform == 'naver' or login_platform == 'ical':				
				try:

					syncInfo = syncLogic.caldav(user,apikey,login_platform,SYNC_TIME_STATE_FORWARD)

				except Exception as e:
					calendarModel.deleteCalendarList(user[0]['account_hashkey'])
					return utils.resCustom(
											201,							
											{'msg':str(e)}
										)					

				if syncInfo['state'] == SYNC_CALDAV_SUCCESS:
					
					return utils.resSuccess(
												{'msg':MSG_SUCCESS_CALDAV_SYNC}
											)
				elif syncInfo['state'] == SYNC_CALDAV_ERR_ALREADY_REIGITER:
					return utils.resCustom(
											201,
											{'msg':syncInfo['data']}
										)							
				else:
					calendarModel.deleteCalendarList(user[0]['account_hashkey'])					
					return utils.resCustom(
											201,
											{'msg':syncInfo['data']}
										)		

			elif login_platform == 'google':

				logging.debug('user==>' + str(user))
				try:

					syncInfo = syncLogic.google(user,apikey,SYNC_TIME_STATE_FORWARD)
					# syncEndRows = syncEndModel.getSyncEnd(user[0]['account_hashkey'],SYNC_END_TIME_STATE_FORWARD)
					# #기존에 동기화 완료된경우이면 패스.
					# if len(syncEndRows) == 0 :
						
					# else:
					# 	return utils.resErr(
					# 							{'msg':MSG_SYNC_ALREADY}
					# 						)	

				except Exception as e:
					calendarModel.deleteCalendarList(user[0]['account_hashkey'])
					return utils.resCustom(
											201,							
											{'msg':str(e)}
										)				
				
				if syncInfo['state'] == SYNC_GOOGLE_SUCCES:					
					return utils.resSuccess(
												{'msg':MSG_SUCCESS_GOOLE_SYNC_LOADING}
											)
				elif syncInfo['state'] == SYNC_CALDAV_ERR_ALREADY_REIGITER:
					return utils.resCustom(
											201,
											{'msg':syncInfo['data']}
										)	
				else:
					calendarModel.deleteCalendarList(user[0]['account_hashkey'])

					#실패한경우는 회원가입은 성공했지만 모종의 이유로 동기화는 실패한 상태다.
					#유저가 다시동기화 할 수 있도록 해주어야한다.
					return utils.resCustom(		
												201,
												{'msg':syncInfo['data']}
											)											


		#watchReciver를 테스트해봐야됨.
		elif action == 'watchReciver':
			
			logging.info('watch')
			logging.info(str(flask.request.headers))				

			
			channel_id = flask.request.headers['X-Goog-Channel-Id']
			state = flask.request.headers['X-Goog-Resource-State']
			account = calendarModel.getAccountHashkey(channel_id)
			
			
			#동기화 할 경우.
			if state == 'sync':

				googleWatchInfoModel.setGoogleWatchInfo(channel_id,GOOGLE_WATCH_ATTACH)
				account_hashkey = account[0]['account_hashkey']	
				calendarModel.updateGoogleSyncState(channel_id,GOOGLE_SYNC_STATE_PUSH_END)						
				calendars = calendarModel.getGoogleSyncState(account_hashkey)
				apikey = flask.request.headers['X-Goog-Channel-Token']

				
				###############
				#####DEBUG#####
				#pushNoti등록을 해제하는 부분입니다. 
				#등록 테스트에서 매번등록되면 나중에 변경됬이력이 생겼을때 등록된 수만큼 푸시가 와서 등록하자마 해제하는 로직.
				###############		

				access_token = account[0]['access_token']		
				resource_id = flask.request.headers['X-Goog-Resource-Id']

				logging.debug('acess_token->'+access_token)
				logging.debug('resource_id->'+resource_id)
				logging.debug('channel_id->'+channel_id)
				# result = gAPI.stopWatch(channel_id,resource_id,access_token)
				
				# if result == "":
				# 	logging.debug('stop watch Succes')
				# else:
				# 	logging.debug('faillllll')

				
				# logging.info('stop noti => ' + result)
				###############
				#####DEBUG#####
				###############		



				is_finished_sync = True
				for calendar in calendars:
					logging.info('google state==>'+str(calendar['google_sync_state']))		
					if calendar['google_sync_state'] != GOOGLE_SYNC_STATE_PUSH_END:
						is_finished_sync = False

					
				if is_finished_sync:
					logging.info('success Sync')

					user_device = userDeviceModel.getPushToken(apikey)
					logging.info('device=> ' + str(user_device))
					#0이 아닐경우는 유저 디바이스가 최초가입으로 제대로 존재할 경우
					if len(user_device) !=0:
						push_token = user_device[0]['push_token']

					#0일경우는 새로운 계정 추가할 경우.					
					
					logging.debug('pushtoken =>' + push_token)
					data_message = {
					    "type" : "sync",
					    "action" : "default"
					}
					
					result = FCM.sendOnlyData(push_token,data_message)

					#푸시보낸후 결과를 몽고디비에 저장.
					#푸시결과,
					#푸시토큰,
					#세션키,
					#데이터메세지
					result['push_token'] = push_token
					result['apikey'] = apikey
					result['push_data'] = data_message
					mFcmModel.insertFcm(result)								
					logging.info(str(result))
					
					statee.userLife(apikey,LIFE_STATE_GOOGLE_PUSH_END)									
					

				else:
					logging.info('fail all sync')
			else:
				rows = calendarModel.getCalendar(channel_id)				
				calendar_hashkey = str(rows[0]['calendar_hashkey'])
				calendar_id = str(rows[0]['calendar_id'])
				

				#해당 캘린더의 최근의 sync토큰을 가져온다.
				row = calendarModel.getLatestSyncToken(calendar_hashkey)
				
				sync_token = row[0]['sync_token'];
				calendar_hashkey = row[0]['calendar_hashkey'];
				calendar_id = row[0]['calendar_id'];
				access_token = account[0]['access_token']
				logging.debug('synctoken =>' + sync_token)
				logging.debug('calendar_id = >'+calendar_id)
				
				
				URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events'
				body = {
					'syncToken':sync_token
				}
				res = json.loads(network_manager.reqGET(URL,access_token,body))				
				logging.debug('new Res' + str(res))

				next_sync_token = res['nextSyncToken']								
				syncModel.setSync(calendar_hashkey,next_sync_token)			

				#기본적으로 아이템에 값이 있어야한다.
				if len(res['items']) != 0:					

					for item in res['items']:
						
						# add/update/delete 모든 공통적인부분 id를 가진다.
						event_id = item['id']
						status = item['status']
						location = None
						recurrence = None

						if('location' in item):
							location = item['location']													

						if 'recurrence' in item:
							logging.debug('rec => '+str(item['recurrence'][0]))			
							recurrence = item['recurrence'][0]														

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
							# logging.debug('created => '+ created)
							# logging.debug('updated => '+ updated)
							# logging.debug('status => ' + status)									
							
						
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

							eventModel.setGoogleEvents(event_hashkey,calendar_hashkey,event_id,summary,start_date,end_date,created,updated,location,recurrence)
							calendarModel.updateCalendarRecoState(calendar_hashkey,CALENDAR_RECO_STATE_DO)
							logging.debug('addEnd')							
							slackAlarmBot.alertEventUpdateEnd("추가")
						#업데이트 한 경우이다. 
						#id값을 찾아서 변환된값을 바꿔준다.
						elif status =='confirmed' and created != updated:
							logging.debug('updated')
							# update events set calendar_id = 'testid', summary = 'sum' where id = '67'
							eventModel.updateEvents(summary,start_date,end_date,created,updated,location,event_id)
							calendarModel.updateCalendarRecoState(calendar_hashkey,CALENDAR_RECO_STATE_DO)
							logging.debug('updateEnd')
							slackAlarmBot.alertEventUpdateEnd("변경")

						elif status == 'cancelled':
							logging.debug('cancelled')							
							eventModel.deleteEvents(event_id)				
			return 'hi'
			
		elif action == 'checkSync':
			
			apikey = flask.request.form['apikey']			
			user_hashkey = redis.get(apikey)
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)
			try:
				user = userAccountModel.getUserAccount(user_hashkey)
				syncEndRows = syncEndModel.getSyncEnd(user[0]['account_hashkey'],SYNC_END_TIME_STATE_FORWARD)
				
				#동기화를 하지 않았다. 
				if len(syncEndRows) == 0 :
					#201은 다시 동기화를 시도해라!
					return utils.resCustom(
												202,
												{'msg':MSG_SYNC_NEED}
											)	
				#동기화를 했다. 	
				#추천이 되어있나 확인한다.
				else:
										
					state = recoModel.checkAllRecoEndState(apikey)									
					if len(state) == 1 and state[0]['reco_state'] == 2:
						return utils.resCustom(
													200,
													{'msg':MSG_RECO_SUCCESS}
												)

					else:
						return utils.resCustom(
													201,
													{'msg':MSG_RECO_ING}
												)							

			except Exception as e:
				return utils.resErr(str(e))		
