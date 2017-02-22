#-*- coding: utf-8 -*-
#author : yenos
#descrip : 멤버의 회원가입, 로그인 및 세션등을 만들어주는 페이지다.
#

import logging
from common import caldavWrapper

from flask.views import MethodView
from common.util import utils
import flask
from common.util import utils

from manager import login_manager
from common.util.statics import *
import json
import datetime

from caldavclient import CaldavClient
from oauth2client import client
from common import gAPI


from model import userDeviceModel
from model import userAccountModel
from model import userModel
from manager.redis import redis

# yenos
# 유저의관한 api 리스트이다.
class Member(MethodView):

	def post(self,action):
		if action == 'loginCheck':
				
			with open('./APP_CONFIGURE.json') as conf_json:
				app_conf = json.load(conf_json)			
			#TODO
			#앱 버전을 꾸준히 체크해줘야한다.
			app_version = flask.request.form['appVersion']
			
			#app_version이 null이거나. 버전이 현재최신이랑 같을경우 는 로그인 로직을탄다.
			if app_version == app_conf['version'] or app_version == 'null':

				who_am_i = login_manager.checkLoginState(flask)									
				logging.debug('whoam_i'+ str(who_am_i))

				if who_am_i['state'] == LOGIN_STATE_AUTO:
					return utils.resSuccess(
												{'msg':'auto login success'}
											)

				elif who_am_i['state'] == LOGIN_STATE_FIRST:
					return utils.resCustom(
												201,
												{'msg':'first sign up'}
											)

				elif who_am_i['state'] == LOGIN_STATE_OTHERDEVICE:
					return utils.resCustom(
												207,
												who_am_i['data']
											)	

				elif who_am_i['state'] == LOGIN_STATE_RELOGIN:				
					return utils.resCustom(
												205,
												who_am_i['data']
											)

				elif who_am_i['state'] == LOGIN_ERROR_INVALID:
					return utils.resErr(
											{'msg':LOGIN_ERROR_INVALID}
										)
				
				elif who_am_i['state'] == LOGIN_ERROR:
					return utils.resErr(
											{'msg':who_am_i['data']}
										)								
			else :
				return utils.resCustom(
											400,
											{'data':'need compulsion update'}
										)

			


			
		elif action == 'signUp':
			
			login_platform = flask.request.form['loginPlatform']
			
			#naver 나 ical일경우, id 와 pw를 받는다.
			if login_platform == 'naver' or login_platform == 'ical':	
				logging.info('naver')
				u_id = flask.request.form['uId']
				u_pw = flask.request.form['uPw']				
				

			elif login_platform == 'google':
				logging.info('google')
				authCode = flask.request.form['authCode']

				try:
					credentials = gAPI.getOauthCredentials(authCode)
				except Exception as e:
					return utils.resErr(	
											{'msg':str(e)}
										)

				access_token = credentials['token_response']['access_token']
				email = credentials['id_token']['email']
				subject = credentials['id_token']['sub']

				#3분정도 여유 시간을 준다. 
				#시간에 타이트하게하면 불안정하다.
				expires_in = int(credentials['token_response']['expires_in']) - EXPIRE_SAFE_RANGE 

				current_date_time = datetime.datetime.now()
				google_expire_time = current_date_time + datetime.timedelta(seconds=expires_in)

				refresh_token = credentials['refresh_token']

				logging.debug('current now => '+str(datetime.datetime.now()))
				logging.debug('credi'+str(credentials))
				logging.debug('accessToken'+access_token)
				logging.debug('extime'+str(google_expire_time))				
				

			gender = flask.request.form['gender']			
			birth = flask.request.form['birth']		
			push_token = flask.request.form['pushToken']
			device_type = flask.request.form['deviceType']
			app_version = flask.request.form['appVersion']
			device_info = flask.request.form['deviceInfo']
			uuid = flask.request.form['uuid']
			sdkLevel = flask.request.form['sdkLevel']

			user_hashkey = utils.makeHashKey(uuid)
			account_hashkey = utils.makeHashKey(user_hashkey)
			device_hashkey = utils.makeHashKey(account_hashkey)
			sessionkey = utils.makeHashKey(device_hashkey)

			try:

				userModel.setUser(user_hashkey,gender,birth)
				
				if login_platform == 'naver' or login_platform == 'ical':
					calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)
					
					principal = calDavclient.getPrincipal()
					homeset = principal.getHomeSet()
					caldav_homeset = homeset.homesetUrl			

					userAccountModel.setCaldavUserAccount(account_hashkey,user_hashkey,login_platform,u_id,u_pw,caldav_homeset)

				elif login_platform =='google':
					#구글에서 email이 userId로 들어간다
					u_id = email
					userAccountModel.setGoogleUserAccount(account_hashkey,user_hashkey,login_platform,u_id,access_token,google_expire_time,subject,refresh_token)

				
				#login_manager
				userDeviceModel.setGoogleUserDevice(device_hashkey,account_hashkey,sessionkey,push_token,device_type,app_version,device_info,uuid,sdkLevel)
				#세션관리를 위해 세션키를 키로 해시키로 매핑시킨다.
				#로그아웃시 해당 세션키를 보내서 날린다.
				
				redis.set(sessionkey,user_hashkey)
				logging.debug('sessionkey' + sessionkey)				
				logging.debug('user_hashkey' + user_hashkey)											

				return utils.resSuccess(
											{'sessionkey':sessionkey}
										)
			except Exception as e:
				return utils.resErr(
										{'msg':str(e)}
									)		

		elif action == 'registerDevice':
			
			sessionkey = flask.request.form['sessionkey']
			push_token = flask.request.form['pushToken']
			device_type = flask.request.form['deviceType']
			app_version = flask.request.form['appVersion']
			device_info = flask.request.form['deviceInfo']			
			uuid = flask.request.form['uuid']
			sdkLevel = flask.request.form['sdkLevel']
			try:

				devices = userDeviceModel.getUserHashkey(sessionkey)

				if len(devices) != 0:
					userHashkey = devices[0]['user_hashkey']
					redis.set(sessionkey,devices[0]['user_hashkey'])

					logging.debug('sessionkey' + sessionkey)
					logging.debug('user_hashkey' + userHashkey)

				userDeviceModel.updateUserDevice(push_token,device_type,app_version,device_info,uuid,sdkLevel,sessionkey)
				return utils.resSuccess({'sessionkey':sessionkey})
			except Exception as e:
				return utils.resErr(str(e))		

		elif action =='updatePushToken':
			push_token = flask.request.form['pushToken']
			sessionkey = flask.request.form['sessionkey']
			
			if not redis.get(sessionkey):
				return utils.resErr(
										{'msg':'invalid sessionkey'}
									)
			try:
				
				userDeviceModel.updatePushToken(push_token,sessionkey)
				return utils.resSuccess(
											{'msg':'success'}
										)

			except Exception as e:

				return utils.resErr(
										{'msg':str(e)}
									)		

		elif action == 'checkVersion':
			app_version = flask.request.form['appVersion']
			sessionkey = flask.request.form['sessionkey']
			
			try:				

				userDeviceModel.setVersion(sessionkey,app_version)				
				return utils.resSuccess(
											{'msg':'successd'}
										)

			except Exception as e:
				return utils.resErr(
										{'msg':str(e)}
									)				
		
		elif action == 'checkAccount':
			sessionkey = flask.request.form['sessionkey']

			if not redis.get(sessionkey):
				return utils.resErr(
										{'msg':'invalid sessionkey'}
									)
			try:
				user_hashkey = redis.get(sessionkey)
				logging.debug('hashkey=> '+user_hashkey)
				accounts = userAccountModel.getHasAccountList(user_hashkey)
				return utils.resSuccess(
											{'data':accounts}
										)

			except Exception as e:
				return utils.resErr(
										{'msg':str(e)}
									)								


			#로그아웃에선 레디스에서 해당 세션키를 날리고, is_active 를 false로
			#서버에서도 날려준다음
			#로그서버에 해당 사항을 저장해준다.			
		elif action == 'logout':

			sessionkey = flask.request.form['sessionkey']
			if not redis.get(sessionkey):
				return utils.resErr(
										{'msg':'invalid sessionkey'}
									)			
			try:
			
				userDeviceModel.logout(sessionkey)
				redis.delete(sessionkey)
				logging.debug('delte sessionkey => ' + sessionkey)									
				return utils.resSuccess(
											{'msg':'logout success'}
										)
			
			except Exception as e:

				return utils.resErr(
										{'msg':str(e)}
									)




			
