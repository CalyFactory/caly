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
from model import supportModel
from model import userAccountModel
from model import userModel
from model import calendarModel
from manager.redis import redis
from common import cryptoo
from common import syncLogic
from common import statee
from common import gAPI
from model import googleWatchInfoModel
from model import syncEndModel

# yenos
# 유저의관한 api 리스트이다.
class Member(MethodView):

	def post(self,action):
		if action == 'loginCheck':
				
			with open('./APP_CONFIGURE.json') as conf_json:
				app_conf = json.load(conf_json)			
			
			with open('./key/conf.json') as conf_json:
				conf = json.load(conf_json)							
			
			current_version = app_conf['version']
			next_version = utils.getNextVersion(current_version)			

			#TODO
			#앱 버전을 꾸준히 체크해줘야한다.
			app_version = flask.request.form['appVersion']

			# logging.info(app_conf['version'][0:4])
			#app_version이 null이거나. 버전이 현재최신이랑 같을경우 는 로그인 로직을탄다.
			if app_version == current_version or app_version == next_version + '_' + conf['versionOpt'] or app_version == 'null':

				who_am_i = login_manager.checkLoginState(flask)									
				logging.info('whoam_i'+ str(who_am_i))

				if who_am_i['state'] == LOGIN_STATE_AUTO:
					
					return utils.resSuccess(
												{'msg':MSG_LOGIN_AUTO}
											)

				elif who_am_i['state'] == LOGIN_STATE_FIRST:
					return utils.resCustom(
												202,
												{'msg':MSG_LOGIN_SIGNUP}
											)

				elif who_am_i['state'] == LOGIN_STATE_OTHERDEVICE:
					return utils.resCustom(
												201,
												who_am_i['data']
											)	

				elif who_am_i['state'] == LOGIN_STATE_RELOGIN:				
					return utils.resCustom(
												200,
												who_am_i['data']
											)
				elif who_am_i['state'] == LOGIN_STATE_RESIGNUP:				
					return utils.resCustom(
												203,
												who_am_i['data']
											)	

				elif who_am_i['state'] == LOGIN_STATE_CHANGEPW:
					return utils.resCustom(
											401,
											{'msg':MSG_LOGIN_NEED_CHANGE_PW}
										)					

				elif who_am_i['state'] == LOGIN_ERROR_INVALID:
					return utils.resCustom(
											401,
											{'msg':MSG_LOGIN_INVALIDIDPW}
										)
				
				elif who_am_i['state'] == LOGIN_ERROR:
					return utils.resErr(
											{'msg':who_am_i['data']}
										)	

			else :
				return utils.resCustom(
											403,
											{'msg':MSG_LOGIN_COMPLUSION_UPDATE}
										)		
			
		elif action == 'signUp':
			
			login_platform = flask.request.form['loginPlatform']
			
			#naver 나 ical일경우, id 와 pw를 받는다.
			if login_platform == 'naver' or login_platform == 'ical':	
				logging.info('naver')
				u_id = flask.request.form['uId']
				u_pw = flask.request.form['uPw']			
				u_pw = cryptoo.encryptt(u_pw)	
				

			elif login_platform == 'google':
				logging.info('google')
				authCode = flask.request.form['authCode']

				try:
					credentials = gAPI.getOauthCredentials(authCode)
				except Exception as e:
					logging.error(str(e))
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

				logging.info('current now => '+str(datetime.datetime.now()))				
				logging.info('extime'+str(google_expire_time))				
				

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
			apikey= utils.makeHashKey(device_hashkey)

			try:

				userModel.setUser(user_hashkey,gender,birth)
				
				if login_platform == 'naver' or login_platform == 'ical':
					calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)
					#여기선 loginmanager를 통과했기때문에 id/pw가 유효한지 체크할 필요가없다.
					principal = calDavclient.getPrincipal()
					homeset = principal.getHomeSet()
					caldav_homeset = homeset.homesetUrl			

					user = userAccountModel.getCaldavUserAccount(u_id,login_platform)
					#검색을 했는데 길이가 0이면, 유저가 없는경우임으로 추가를 해준다.
					if len(user) == 0:
						
						userAccountModel.setCaldavUserAccount(account_hashkey,user_hashkey,login_platform,u_id,u_pw,caldav_homeset)
					#유저가 존재하면 이미 등록된 아이디라고 알려준다.
					else:		
						return utils.resCustom(
												403,
												{'msg':MSG_FAILE_ADD_ACCOUNT_REGISTERD}
											)					

				elif login_platform =='google':
					#구글에서 email이 userId로 들어간다
					u_id = email
					userAccountModel.setGoogleUserAccount(account_hashkey,user_hashkey,login_platform,u_id,access_token,google_expire_time,subject,refresh_token)

				
				#login_manager
				userDeviceModel.setGoogleUserDevice(device_hashkey,account_hashkey,apikey,push_token,device_type,app_version,device_info,uuid,sdkLevel)
				#세션관리를 위해 세션키를 키로 해시키로 매핑시킨다.
				#로그아웃시 해당 세션키를 보내서 날린다.
				
				redis.set(apikey,user_hashkey)
				logging.info('apikey' + apikey)				
				logging.info('user_hashkey' + user_hashkey)	
				
				#로그인이 끝났다면!
				#로그인끝난상황을 기록한다.
				statee.userLife(apikey,LIFE_STATE_SIGNUP)

				return utils.resSuccess(
											{'apikey':apikey}
										)
			except Exception as e:
				logging.error(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)		
		elif action == 'updateAccount':

			login_platform = flask.request.form['loginPlatform']
			if login_platform == 'naver' or login_platform == 'ical':	
				
				u_id = flask.request.form['uId']
				u_pw = flask.request.form['uPw']			
				u_pw = cryptoo.encryptt(u_pw)
				try:
					calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)
					principal = calDavclient.getPrincipal()					
					userAccountModel.updateCaldavUserAccount(u_id,u_pw,login_platform)
				
				except Exception as e:
					logging.error(str(e))
					#그래도 비밀번호가 또 틀렸을경우 401을 리턴한다.
					if str(e) == 'user auth error':
						return utils.resCustom(
											401,
											{'msg':str(e)}
										)

					return utils.resErr(
										{'msg':str(e)}
									)

				return utils.resSuccess(
											{'msg':'success!'}
										)				


		elif action == 'registerDevice':
			
			apikey = flask.request.form['apikey']
			push_token = flask.request.form['pushToken']
			device_type = flask.request.form['deviceType']
			app_version = flask.request.form['appVersion']
			device_info = flask.request.form['deviceInfo']			
			uuid = flask.request.form['uuid']
			sdkLevel = flask.request.form['sdkLevel']

			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)

			try:

				devices = userDeviceModel.getUserHashkey(apikey)

				if len(devices) != 0:
					user_hashkey = devices[0]['user_hashkey']
					redis.set(apikey,devices[0]['user_hashkey'])

					logging.info('apikey' + apikey)
					logging.info('user_hashkey' + user_hashkey)

				userDeviceModel.updateUserDevice(push_token,device_type,app_version,device_info,uuid,sdkLevel,apikey)
				userModel.updateUserIsActive(user_hashkey,1)
				statee.userLife(apikey,LIFE_STATE_REGISTER_DEVICE)
				
				return utils.resSuccess(
											{'apikey':apikey}
										)
			except Exception as e:
				logging.error(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)		


		elif action == 'checkVersion':
			app_version = flask.request.form['appVersion']
			apikey = flask.request.form['apikey']
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)
			
			try:				

				userDeviceModel.setVersion(apikey,app_version)				
				return utils.resSuccess(
											{'msg':'successd'}
										)

			except Exception as e:
				logging.error(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)											
		elif action == 'removeAccount':	

			try:
				apikey = flask.request.form['apikey']			
				login_platform = flask.request.form['loginPlatform']	
				user_hashkey = redis.get(apikey)
				logging.info('user_hashkey = '+ user_hashkey)
				if not user_hashkey:
					return utils.resErr(
											{'msg':MSG_INVALID_TOKENKEY}
										)

				#현재 로그인한 계정인지를 확인. 
				u_id = flask.request.form['uId']
				#세션에 잡혀있는 유저
				api_user = userDeviceModel.getUserWithApikey(apikey)
				real_user = userAccountModel.getUserAccountPlatform(u_id,login_platform)
				
				logging.info('remove User => '+str(api_user))
				logging.info('remove User => '+str(api_user[0]['user_id']))

				# user_iduser[0]['user_id']
				#현재 apikey로 id와 플랫폼이 같다면 ==> 현재 로그인되어있는 계정을 지우려한다 			
				#다른 남아있는 account로 연결시켜줘야한다. 
				#만약 로그인 플랫폼이 구글이면 와치를 떼어내야한다. 
				if login_platform == 'google':
					
					logging.info('realuser =>'+str(real_user[0]))
					google_calendars = calendarModel.getGoogleCalendarInfoWithAccountHashkey(real_user[0]['account_hashkey'])
					for google_calendar in google_calendars:
						#액세스토큰이 만료되어 다시받게되는경우!!!
						#최초 1회때 액세스토큰을 이용하면안되고
						#새로 발급받은 accessToken을 이용하여야한다.
						#매번 새로운 accessToken을 요청한다. 						
						
						result = gAPI.stopWatch(google_calendar['google_channel_id'],google_calendar['google_resource_id'],real_user[0]['account_hashkey'])
						
						if result == "":
							logging.info('stop watch Succes')
							googleWatchInfoModel.setGoogleWatchInfo(google_calendar['google_channel_id'],GOOGLE_WATCH_DETACH)
						else:
							logging.info('faillllll')						

				#api에 있는 유저와 실제 넘겨저온 데이터가 같다면 api를 바꿔줘야함. 나머지는 실유저로 작업해야함. 
				if u_id == api_user[0]['user_id'] and login_platform == api_user[0]['login_platform']:

					logging.info('current connection user')

					anotherUsers = userAccountModel.getAnotherConnectionUser(user_hashkey,u_id)
					#연결된 다른 해시키로 업데이트 시켜준다.
					userDeviceModel.setAnotherConnectionUser(anotherUsers[0]['account_hashkey'],apikey)

				
					

				#현재유저의 어카운트 해시키를 가지고
				account_hashkey = real_user[0]['account_hashkey']
				#디바이스 정보를 날리진 않는다.남아있는계정이 있기떄문에
				
				# #캘린더에서 필요없는것들을 날린다. 
				#그냥 해시키를 다 날려버림..
				calendarModel.withdraw(account_hashkey)		
				#유저를 3으로 바꾸지도않는다 계정만 삭제함으로
				
				#유저의 개인정보는 날려야한다.
				userAccountModel.withdrawWithAccountHashkey(account_hashkey)
				statee.userLife(apikey,LIFE_STATE_REMOVE_ACCOUNT)
				
				return utils.resSuccess(
											{'msg':MSG_WITHDRAWL_SUCCESS}
										)
			
			except Exception as e:
				logging.info(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)				
		

		elif action == 'addAccount':
			apikey = flask.request.form['apikey']			
			login_platform = flask.request.form['loginPlatform']	

			user_hashkey = redis.get(apikey)
			logging.info('user_hashkey = '+ user_hashkey)
			if not user_hashkey:
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)

			account_hashkey = utils.makeHashKey(user_hashkey)
			
			statee.userLife(apikey,LIFE_STATE_ADDACCOUNT)
			
			if login_platform == 'naver' or login_platform == 'ical':	
				#caldav일경우.
				u_id = flask.request.form['uId']
				u_pw = flask.request.form['uPw']
				u_pw = cryptoo.encryptt(u_pw)
				try:
					calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)									

					try:
						principal = calDavclient.getPrincipal()				
					except Exception as e:
						logging.error(str(e))
						return utils.resCustom(
													401,
													{'msg':'invalid id/pw'}
											)

					homeset = principal.getHomeSet()
					caldav_homeset = homeset.homesetUrl	

					logging.info('caldav_hoemse =>' + caldav_homeset)
					

					user = userAccountModel.getCaldavUserAccount(u_id,login_platform)
					#검색을 했는데 길이가 0이면, 유저가 없는경우임으로 추가를 해준다.
					#그리고 동기화로직을 탄다.
					logging.info('user = >'+str(user))

					if len(user) == 0:

						userAccountModel.setCaldavUserAccount(account_hashkey,user_hashkey,login_platform,u_id,u_pw,caldav_homeset)
						
						#다시 유저가생겼음으로 유저를 가져와서 접속한다.
						user = userAccountModel.getCaldavUserAccount(u_id,login_platform)

					#유저가 존재하면 이미 등록된 아이디라고 알려준다.
					else:		
						return utils.resCustom(
												403,
												{'msg':MSG_FAILE_ADD_ACCOUNT_REGISTERD}
											)

					
					#가입이 완료되었다면 동기화 로직을 돈다.
					#기존 위의 파라미터로도 접속은 가능하지만. 
					# sync 기본 요청에서는 user로 값을 넣어줘야함으로 맞춰줘야함.
					try:
					#일단 캘린더리스트를 삭제하고..					
						syncInfo = syncLogic.caldav(user,user_hashkey,login_platform,SYNC_TIME_STATE_FORWARD)
					except Exception as e:
						logging.error(str(e))
						calendarModel.deleteCalendarList(user[0]['account_hashkey'])
						return utils.resCustom(
												201,							
												{'msg':str(e)}
											)							

					if syncInfo['state'] == SYNC_CALDAV_SUCCESS:	
						statee.userLife(apikey,LIFE_STATE_ADDACCOUNT_END)
						
						return utils.resSuccess(
													{'msg':MSG_SUCCESS_ADD_ACCOUNT}
												)

					else:
						calendarModel.deleteCalendarList(user[0]['account_hashkey'])
						#codeReview
						#최소 에러라인을 알려주면 서로편할것이다.
						return utils.resCustom(		
													201,
													{'msg':str(syncInfo['data'])}
												)																
				except Exception as e:
					logging.error(str(e))
					return utils.resErr(
											{'msg':str(e)}
										)	


			elif login_platform =='google':

				authCode = flask.request.form['authCode']

				try:
					credentials = gAPI.getOauthCredentials(authCode)
			

					subject = credentials['id_token']['sub']					
					user = userAccountModel.getGoogleUserAccount(subject)

					#subject가 일치하는 항목이 있다면 이미 등록한것.
					if len(user) != 0:
						return utils.resCustom(
												403,
												{'msg':MSG_FAILE_ADD_ACCOUNT_REGISTERD}
											)
						
					access_token = credentials['token_response']['access_token']
					email = credentials['id_token']['email']

					#3분정도 여유 시간을 준다. 
					#시간에 타이트하게하면 불안정하다.
					expires_in = int(credentials['token_response']['expires_in']) - EXPIRE_SAFE_RANGE 

					current_date_time = datetime.datetime.now()
					google_expire_time = current_date_time + datetime.timedelta(seconds=expires_in)

					#codeReview
					#리프레시토큰 재발급
					refresh_token = credentials['refresh_token']

					logging.info('current now => '+str(datetime.datetime.now()))

					logging.info('refreshTOken'+str(refresh_token))

					#구글에서 email이 userId로 들어간다
					u_id = email
					#회원가입					
					userAccountModel.setGoogleUserAccount(account_hashkey,user_hashkey,login_platform,u_id,access_token,google_expire_time,subject,refresh_token)
					
					user = userAccountModel.getGoogleUserAccount(subject)
					
					logging.info('user==>'+str(user))

					try:
						syncInfo = syncLogic.google(user,apikey,SYNC_TIME_STATE_FORWARD)
					except Exception as e:
						logging.error(str(e))
						calendarModel.deleteCalendarList(user[0]['account_hashkey'])
						return utils.resCustom(
												201,							
												{'msg':str(e)}
											)						
					
					logging.info('syncInfo==>'+str(syncInfo))

					if syncInfo['state'] == SYNC_GOOGLE_SUCCES:
						statee.userLife(apikey,LIFE_STATE_ADDACCOUNT_END)					

						return utils.resSuccess(
													{'msg':MSG_SUCCESS_ADD_ACCOUNT}
												)

					else:
						calendarModel.deleteCalendarList(user[0]['account_hashkey'])
						#실패한경우는 회원가입은 성공했지만 모종의 이유로 동기화는 실패한 상태다.
						#유저가 다시동기화 할 수 있도록 해주어야한다.
						return utils.resCustom(		
													201,
													{'msg':str(syncInfo['data'])}
												)							

				except Exception as e:
					logging.error(str(e))
					return utils.resErr(	
											{'msg':str(e)}
										)	
			#로그아웃에선 레디스에서 해당 세션키를 날리고, is_active 를 false로
			#서버에서도 날려준다음
			#로그서버에 해당 사항을 저장해준다.			
		elif action == 'logout':

			apikey = flask.request.form['apikey']
			if not redis.get(apikey):
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)			
			try:
			
				userDeviceModel.logout(apikey)
				redis.delete(apikey)
				logging.info('delete apikey => ' + apikey)									
				
				statee.userLife(apikey,LIFE_STATE_LOGOUT)
				
				return utils.resSuccess(
											{'msg':MSG_LOGOUT_SUCCESS}
										)
			
			except Exception as e:
				logging.error(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)
		elif action == 'withdrawal':

			apikey = flask.request.form['apikey']
			contents = flask.request.form['contents']
			

			user_hashkey = redis.get(apikey)
			if not user_hashkey:
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)			
			try:
				user = userAccountModel.getUserLoginPlatform(apikey)

				if user[0]['login_platform'] == 'google':
					#!!!! TODO
					#account_hashkey!!!가 apikey에만 종속되어있다.
					#회원탈퇴시 모든 계정에서 watch가 떼어져야한다.
					google_calendars = calendarModel.getGoogleCalendarInfo(apikey)					
					for google_calendar in google_calendars:
						result = gAPI.stopWatch(google_calendar['google_channel_id'],google_calendar['google_resource_id'],google_calendar['account_hashkey'])
						
						if result == "":
							logging.info('stop watch Succes')
							googleWatchInfoModel.setGoogleWatchInfo(google_calendar['google_channel_id'],GOOGLE_WATCH_DETACH)
						else:
							logging.info('faillllll')						

						logging.info('result => '+result)

				
				users = userAccountModel.getUserAccount(user_hashkey)	
				#사유는 한번만 받을수 있도록한다.
				supportModel.setRequests(apikey,users[0]['account_hashkey'],contents,REQUESTS_TYPE_WITHDRAWAL)
				#유저해시키에 여러개가있을 수있다.
				for user in users:			
					account_hashkey = user['account_hashkey']
					#3. 해당유저의 모든디바이스 정보에서 개인정보값을 날린다
					userDeviceModel.withdraw(account_hashkey)
					#캘린더에서 필요없는것들 제검ㅊ
					calendarModel.withdraw(account_hashkey)
							
				#공통적으로 날려야 할것들
				#1. 해당유저의 모든계저의 isactive값을 3으로한다.
				userModel.updateUserIsActive(user_hashkey,3)
				#2. 해당유저의 모든계정의 개인정보 값을 날린다.
				userAccountModel.withdraw(user_hashkey)
				
				#2. api key remove
				apikeys = userDeviceModel.getUserApikeyList(user_hashkey)
				statee.userLife(apikey,LIFE_STATE_WITHDRAWAL)
				
				#################				
				#######google일 경우 calendar push 알림 제거

				for apikey in apikeys:
					redis.delete(apikey['apikey'])					
				
				
				
				return utils.resSuccess(
											{'msg':MSG_WITHDRAWL_SUCCESS}
										)
			
			except Exception as e:
				logging.info(str(e))
				return utils.resErr(
										{'msg':str(e)}
									)				
		elif action == 'accountList':
			apikey = flask.request.form['apikey']
			user_hashkey = redis.get(apikey)
			
			if not user_hashkey:			
				return utils.resErr(
										{'msg':MSG_INVALID_TOKENKEY}
									)			
			try:
				syncAccountList = syncEndModel.getAccountLatestSyncTime(apikey,user_hashkey)
				return utils.resSuccess(
											{'data':syncAccountList}
										)

			except Exception as e:
				return utils.resCustom(
										400,							
										{'msg':str(e)}
									)			
