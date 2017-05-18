#-*- coding: utf-8 -*-

import json
import urllib
import flask
import logging

from flask.views import MethodView
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
from manager import network_manager

from datetime import timedelta,datetime
from model import mFcmModel
from manager.redis import redis
from common.util.statics import *
from common import gAPI

from model import mFcmModel
from time import gmtime, strftime
from model import mLog

class Log(MethodView):
#sync는 캘린더 리스트 가져오기 => 이벤트리스트 저장하기.(최신기록 먼저)

	def post(self,action):
		if action == 'screen':
			log_result = {}


			apikey = 'None'
			user_info = 'None'
			if 'apikey' in flask.request.form.keys():
				apikey = flask.request.form['apikey']


			sessionKey = flask.request.form['sessionKey']
			screenName = flask.request.form['screenName']
			status = int(flask.request.form['status'])
			
			if apikey is not 'None':
				if not redis.get(apikey):
					return utils.resErr(
											{'msg':MSG_INVALID_TOKENKEY}
										)

			if status == 1:
				status = "onStart"
			elif status == 2:
				status = "onStop"

			#기본정보세팅
			log_result = mLog.getUserInfo(apikey)			
			log_result['sessionKey'] = sessionKey
			log_result['screenName'] = screenName
			log_result['status'] = status
			
			

			mLog.insertLog(MONGO_COLLECTION_SCREEN_LOG,log_result)
			return utils.resSuccess(									
										{'data':'succes'}
									)
