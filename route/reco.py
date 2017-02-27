from manager import db_manager
from flask.views import MethodView
from model import recoModel

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





