from manager import db_manager
from flask.views import MethodView
from model import recoModel
from model import userDeviceModel

from common.util import utils
from manager.redis import redis
import flask
import logging
from common.util.statics import *

from datetime import datetime

class Reco(MethodView):
	def post(self,action):
		if action == 'getList':
			apikey = flask.request.form['apikey']
			eventHashkey = flask.request.form['eventHashkey']
			category = flask.request.form['category']

			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)	

			try:												
				recoList = recoModel.getRecoList(eventHashkey,category)
			except Exception as e:
				return utils.resErr(str(e))		

			if len(recoList) != 0:
				return utils.resSuccess(
											{'data':recoList}
										)
			else:
				return utils.resCustom(
											201,
											{'msg':MSG_RECO_END}
										)				

		elif action == 'tracking':
			apikey = flask.request.form['apikey']
			reco_hashkey = flask.request.form['recoHashkey']
			event_hashkey = flask.request.form['eventHashkey']
			typee = flask.request.form['type']
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)	

			try:
				account_hashkey = userDeviceModel.getUserAccountHashkey(apikey)[0]['account_hashkey']
				# print(account_hashkey[0])
				# logging.debug(account_hashkey[0]['account_hashkey'])
				recoModel.trackingReco(apikey,reco_hashkey,event_hashkey,account_hashkey,typee)			
				return utils.resSuccess(
											{'data':'successInsert'}
										)
			except Exception as e:
				return utils.resErr(str(e))					

		elif action == 'checkRecoState':
			apikey = flask.request.form['apikey']			
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)		
			try:

				state = recoModel.checkAllRecoEndState(apikey)
				print(state)

			except Exception as e:
				return utils.resErr(str(e))		
			
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





