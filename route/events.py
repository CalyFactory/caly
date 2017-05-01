from manager import db_manager
from flask.views import MethodView
from model import eventModel
from model import userAccountModel
from model import userDeviceModel

from common.util import utils
from manager.redis import redis
import flask
import logging
from common.util.statics import *

from datetime import datetime
from model import mLog

class Events(MethodView):
	def post(self,action):
		if action == 'getList':
			apikey = flask.request.form['apikey']
			pageNum = flask.request.form['pageNum']			
			user_hashkey = redis.get(apikey)
			current_time = datetime.now()

			logging.info('userHashkey=>' + str(user_hashkey))
			logging.info('pageNum=>' + pageNum)	
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)
			try:
				# account_hashkey = userDeviceModel.getUserAccountHashkey(apikey)[0]['account_hashkey']
				logging.info('syncolderTIme => '+str(userDeviceModel.getUserSyncOlderTime(user_hashkey)))
				#전체 계정중에 가장 오래된일자를 기준으로 이벤트리스트에서 보여주어야한다
				account_hashkey = userDeviceModel.getUserSyncOlderTime(user_hashkey)[0]['account_hashkey']
				

				if int(pageNum) == 0 :

					logging.info('call first Events')
					rows = eventModel.getEventsFirst(account_hashkey,user_hashkey,current_time,EVENTS_FORWARD_CNT,EVENTS_BACKWARD_CNT)
					logging.info('events ===> '+str(rows))

				elif int(pageNum) > 0 :
					logging.info('call forward')
					#2개씩 보여준다.
					rangee = EVENTS_ITEM_CNT
					#기존 보여줬던 이벤트를 제외한 데이터를 요청하기위해 EVENTS_FORWARD_CNT 만큼 offset을 땡겨준다.
					pager = (int(pageNum)-1) * int(rangee) + EVENTS_FORWARD_CNT

					rows = eventModel.getEventsForward(user_hashkey,current_time,pager,rangee)
					
				elif int(pageNum) < 0 :
					logging.info('call backward')
					
					rangee = EVENTS_ITEM_CNT
					
					pageNum = int(pageNum)*(-1)
					
					pager = (int(pageNum)-1) * int(rangee) + EVENTS_BACKWARD_CNT				

					logging.info('pageNum => '+ str(pageNum))
					logging.info('pager => '+ str(pager))
					rows = eventModel.getEventsBackward(user_hashkey,current_time,pager,rangee,account_hashkey)
				
			except Exception as e:
				logging.error(str(e))
				return utils.resErr({'msg':str(e)})		

			if len(rows) != 0:
				return utils.resSuccess(
											{'data':rows}
										)

			else:
				return utils.resCustom(
											201,
											{'msg':MSG_EVENTS_END}
										)
		
		elif action == 'setLog':
			log_result = {}

			apikey = flask.request.form['apikey']
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)

			event_hashkey = None
			if 'eventHashkey' in flask.request.form.keys():
				residense_time = flask.request.form['eventHashkey']

			#0은 클릭.			
			category = int(flask.request.form['category'])
			action = int(flask.request.form['action'])
			label = int(flask.request.form['label'])

			if category == 0:
				category = 'eventView'
				
				if label == 0:
					label = 'banner'				
				elif label == 1:
					label = 'refresh'	


			elif category == 1:
				category = 'eventcell'
				if label == 0:
					label = 'cell'								

			if action == 0:
				action = 'click'



			#기본정보세팅
			log_result = mLog.getUserInfo(apikey)
			log_result['event_hashkey'] = event_hashkey
			log_result['category'] = category
			log_result['label'] = label			
			log_result['action'] = action
			
			

			mLog.insertLog(MONGO_COLLECTION_EVENT_LOG,log_result)
			return utils.resSuccess(									
										{'data':'succes'}
									)

			


