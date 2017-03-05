from manager import db_manager
from flask.views import MethodView

from model import supportModel
from model import userAccountModel

from common.util import utils
from manager.redis import redis
import flask
import logging
from common.util.statics import *

from datetime import datetime

class Support(MethodView):
	def post(self,action):
		if action == 'notices':
			apikey = flask.request.form['apikey']
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)
			try:
				notices = supportModel.getNotice()
			except Exception as e:
				return utils.resErr(str(e))		

			if len(notices) != 0:
				return utils.resSuccess(
											{'data':notices}
										)
			else:
				return utils.resErr(
										{'msg':MSG_DATA_NONE}
									)
		elif action == 'requests':
			apikey = flask.request.form['apikey']
			contents = flask.request.form['contents']
			user_hashkey = redis.get(apikey)
			
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)
			try:
				print(user_hashkey)
				user = userAccountModel.getUserAccount(user_hashkey)
				print(user)
				account_hashkey = user[0]['account_hashkey']
				rows = supportModel.setRequests(apikey,account_hashkey,contents)
				return utils.resSuccess(
											{'msg':MSG_SUCCESS}
										)				
			except Exception as e:
				return utils.resErr(
										{'msg':str(e)}
									)		

			


			


