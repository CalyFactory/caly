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
from model import mLog


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
				return utils.resErr(
										{'msg':str(e)}
									)		

			if len(recoList) != 0:
				return utils.resSuccess(
											{'data':recoList}
										)
			else:
				return utils.resCustom(
											201,
											{'msg':MSG_RECO_END}
										)				
		elif action == 'setLog':
			log_result = {}

			apikey = flask.request.form['apikey']
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)

			event_hashkey = flask.request.form['eventHashkey']
			reco_hashkey = None
			residense_time = None

			#만약 residenseTime이 존재하면 넣고 아니면 None
			if 'residenseTime' in flask.request.form.keys():
				residense_time = flask.request.form['residenseTime']

			if 'recoHashkey' in flask.request.form.keys():
				reco_hashkey = flask.request.form['recoHashkey']

			
			category = int(flask.request.form['category'])
			action = int(flask.request.form['action'])
			label = int(flask.request.form['label'])

			#view일 경우
			if category == 0:
				category = 'recoView'

				if label == 0:
					label = 'allMap'
				elif label == 1:
					label = 'restaurant'					
				elif label == 2:
					label = 'cafe'										
				elif label == 3:
					label = 'place'															
			
			#cell일 경우 
			elif category == 1:
				category = 'recoCell'
				if label == 0:
					label = 'blog'
				if label == 1:
					label = 'itemMap'
				if label == 2:
					label = 'sharingKakao'										
			
				

			if action == 0:
				action = 'click'	
			
			log_result = mLog.getUserInfo(apikey)


			log_result['event_hashkey'] = event_hashkey
			log_result['reco_hashkey'] = reco_hashkey
			log_result['residense_time'] = residense_time
			log_result['category'] = category
			log_result['label'] = label			
			log_result['action'] = action


			mLog.insertLog(MONGO_COLLECTION_RECO_LOG,log_result)
			return utils.resSuccess(									
										{'data':'succes'}
									)


		elif action == 'tracking':
			apikey = flask.request.form['apikey']
			reco_hashkey = flask.request.form['recoHashkey']
			event_hashkey = flask.request.form['eventHashkey']
			typee = flask.request.form['type']
			residense_time = None
			residense_time = flask.request.form['residenseTime']
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)	

			try:
				account_hashkey = userDeviceModel.getUserAccountHashkey(apikey)[0]['account_hashkey']				
				recoModel.trackingReco(apikey,reco_hashkey,event_hashkey,account_hashkey,typee,residense_time)			
				return utils.resSuccess(
											{'data':'successInsert'}
										)
			except Exception as e:
				logging.error(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)					

		elif action == 'checkRecoState':
			apikey = flask.request.form['apikey']			
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)		
			try:

				state = recoModel.checkAllRecoEndState(apikey)				

			except Exception as e:
				logging.error(str(e))
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





