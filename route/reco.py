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
		# elif action == 'getAutoList':
			
		# 	category = flask.request.form['category']
		# 	data = {
		# 		"restaurant":[
		# 			{
		# 			"no" : 0,
		# 			"reco_hashkey" : "95534fec-cf7a-4156-8d39-bbb9aec91344"
		# 			},
		# 			{
		# 			"no" : 1,
		# 			"reco_hashkey" : "b2da7e49-49d7-4cd1-9e69-76fd20b8dd42"
		# 			}					
		# 		],
		# 		"cafe": [
		# 			{
		# 			"no" : 0,
		# 			"reco_hashkey" : "75689e92-5b17-4928-a341-aa1e7f78138e"
		# 			},
		# 			{
		# 			"no" : 1,
		# 			"reco_hashkey" : "75458fb0-a33e-41b1-89bf-fad7987d20c6"
		# 			}									
		# 		],
		# 		"place":[
		# 			{
		# 			"no" : 0,
		# 			"reco_hashkey" : "ee7bfecd-8068-4b24-922a-80ccd2e84f2d"
		# 			},
		# 			{
		# 			"no" : 1,
		# 			"reco_hashkey" : "f140216f-5539-4e25-a8d3-7dd64b99d8a5"
		# 			}													
		# 		]
		# 	}



		elif action == 'setLog':
			log_result = {}

			apikey = flask.request.form['apikey']
			sessionKey = flask.request.form['sessionKey']

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
				#지도로보기눌렀을경우
				if label == 0:
					label = 'fullMap'
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
					label = 'deepLink'
				elif label == 1:
					label = 'itemMap'
				elif label == 2:
					label = 'sharingKakaoInCell'
				elif label == 3:
					label = 'sharingKakaoInBlog'	


			#맵뷰일경우
			elif category == 2:
				category = 'recoMapView'
				if label == 0:
					label = 'myLocation'
				elif label == 1:
					label = 'filterAll'						
				elif label == 2:
					label = 'filterRestaurant'					
				elif label == 3:
					label = 'filterCafe'										
				elif label == 4:
					label = 'filterPlace'		
			#map detail cell
			elif category == 3:
				category = 'recoMapCell'
				if label == 0:
					label = 'deepLink'
				elif label == 1:
					label = 'sharingKakaoInCell'
				
			

			if action == 0:
				action = 'click'	
			
			log_result = mLog.getUserInfo(apikey)


			log_result['eventHashkey'] = event_hashkey
			log_result['recoHashkey'] = reco_hashkey
			log_result['residenseTime'] = residense_time
			log_result['category'] = category
			log_result['label'] = label			
			log_result['action'] = action
			log_result['sessionKey'] = sessionKey


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





