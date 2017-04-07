from manager import db_manager
from flask.views import MethodView

from common.util import utils
from manager.redis import redis
import flask
import logging
from common.util.statics import *
from model import userDeviceModel

from datetime import datetime

class Setting(MethodView):
	def post(self,action):
		if action == 'setReceivePush':

			apikey = flask.request.form['apikey']
			receive = flask.request.form['receive']
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)
			try:
				
				userDeviceModel.setRecviePush(apikey,receive)

				return utils.resSuccess(
											{'msg':'success'}
										)

			except Exception as e:
				logging.error(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)				
			pass

		elif action =='updatePushToken':
			push_token = flask.request.form['pushToken']
			apikey = flask.request.form['apikey']
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)
			try:
				
				userDeviceModel.updatePushToken(push_token,apikey)
				return utils.resSuccess(
											{'msg':'success'}
										)

			except Exception as e:
				logging.error(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)		
