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

class Events(MethodView):
	def post(self,action):
		if action == 'getList':
			apikey = flask.request.form['apikey']
			pageNum = flask.request.form['pageNum']			
			user_hashkey = redis.get(apikey)
			current_time = datetime.now()

			logging.debug('userHashkey=>' + str(user_hashkey))
			logging.debug('pageNum=>' + pageNum)	
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)
			try:
				account_hashkey = userDeviceModel.getUserAccountHashkey(apikey)[0]['account_hashkey']

				if int(pageNum) == 0 :

					logging.debug('call first Events')
					rows = eventModel.getEventsFirst(account_hashkey,user_hashkey,current_time,EVENTS_FORWARD_CNT,EVENTS_BACKWARD_CNT)

				elif int(pageNum) > 0 :
					logging.debug('call forward')
					#2개씩 보여준다.
					rangee = EVENTS_ITEM_CNT
					#기존 보여줬던 이벤트를 제외한 데이터를 요청하기위해 EVENTS_FORWARD_CNT 만큼 offset을 땡겨준다.
					pager = (int(pageNum)-1) * int(rangee) + EVENTS_FORWARD_CNT

					rows = eventModel.getEventsForward(user_hashkey,current_time,pager,rangee)
					
				elif int(pageNum) < 0 :
					logging.debug('call backward')
					
					rangee = EVENTS_ITEM_CNT
					
					pageNum = int(pageNum)*(-1)
					
					pager = (int(pageNum)-1) * int(rangee) + EVENTS_BACKWARD_CNT				

					rows = eventModel.getEventsBackward(user_hashkey,current_time,pager,rangee,account_hashkey)
				
			except Exception as e:
				return utils.resErr(str(e))		

			if len(rows) != 0:
				return utils.resSuccess(
											{'data':rows}
										)

			else:
				return utils.resCustom(
											201,
											{'msg':MSG_EVENTS_END}
										)
		



			


