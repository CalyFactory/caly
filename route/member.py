#-*- coding: utf-8 -*-
#author : yenos
#descrip : 멤버의 회원가입, 로그인 및 세션등을 만들어주는 페이지다.
#
#TODO!!!
#NOSQL로 세션로그를 관리해줘야한다
#(언제 세션이 끊기고(로그아웃) 언제다시연결됬는지 등의 정보)

from flask.views import MethodView
from common.util import utils
from manager import db_manager
import flask
from common.util import utils
from manager.redis import redis
from manager import login_manager
from manager import network_manager
from common.util.statics import *
import json
import datetime

from caldavclient import CaldavClient
from oauth2client import client

# yenos
# 유저의관한 api 리스트이다.
class Member(MethodView):

	def post(self,action):
		if action == 'loginCheck':
			#TODO
			#앱 버전을 꾸준히 체크해줘야한다.
			#app_version = flask.request.form['app_version']						
			print('hig')
			# try:
			who_am_i = login_manager.checkLoginState(flask)									
							
			if who_am_i['state'] == LOGIN_STATE_AUTO:
				return utils.resSuccess('auto login success')

			elif who_am_i['state'] == LOGIN_STATE_FIRST:
				return utils.resCustom(201,'first sign up')

			elif who_am_i['state'] == LOGIN_STATE_OTHERDEVICE:
				return utils.resCustom(207,who_am_i['data'])	

			elif who_am_i['state'] == LOGIN_STATE_RELOGIN:				
				return utils.resCustom(205,who_am_i['data'])

			elif who_am_i['state'] == LOGIN_ERROR_INVALID:
				return utils.resErr(LOGIN_ERROR_INVALID)
			
			elif who_am_i['state'] == LOGIN_ERROR:
				return utils.resErr(who_am_i['data'])
			
		elif action == 'signUp':
			
			login_platform = flask.request.form['loginPlatform']
			print('signup'+login_platform)
			#naver 나 ical일경우, id 와 pw를 받는다.
			if login_platform == 'naver' or login_platform == 'ical':	
				print('naver')
				u_id = flask.request.form['uId']
				u_pw = flask.request.form['uPw']				
				gender = flask.request.form['gender']

			elif login_platform == 'google':
				print('google')
				authCode = flask.request.form['authCode']
				
				flow = client.flow_from_clientsecrets(
					
					'./key/client_secret.json',
					scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.profile  https://www.googleapis.com/auth/calendar.readonly',
					redirect_uri='https://ssoma.xyz:55566/googleAuthCallBack'
				)				
				credentials = json.loads(flow.step2_exchange(authCode).to_json())
				access_token = credentials['token_response']['access_token']

				current_date_time = datetime.datetime.now()
				google_expire_time = current_date_time + datetime.timedelta(seconds=credentials['token_response']['expires_in'])
				
				print('current now => '+str(datetime.datetime.now()))
				print('credi'+str(credentials))
				print('accessToken'+access_token)
				print('extime'+str(expired_date_time))
				
				# redis.set('user_access_token',access_token)				

				URL = 'https://www.googleapis.com/oauth2/v1/userinfo'		
				res = network_manager.reqGET(URL,access_token)
				print('userInfo = '+res)
				user_gender = json.loads(res)['gender']				
				print('user_gender = '+user_gender)
				if user_gender == 'male':	
					gender = 1
				elif user_gender == 'female':
					gender = 2



			birth = flask.request.form['birth']		
			push_token = flask.request.form['pushToken']
			device_type = flask.request.form['deviceType']
			app_version = flask.request.form['appVersion']
			device_info = flask.request.form['deviceInfo']
			uuid = flask.request.form['uuid']

			user_hashkey = utils.makeHashKey(uuid)
			account_hashkey = utils.makeHashKey(user_hashkey)
			device_hashkey = utils.makeHashKey(account_hashkey)
			session_key = utils.makeHashKey(device_hashkey)

			try:
				db_manager.query(
					"INSERT INTO USER " 
					"(user_hashkey,user_gender,user_birth)"
					"VALUES"
					"(%s, %s, %s)",
					(			
						user_hashkey,
						gender,
						birth
					)
				)

				#TODO
				#calendar HomeSat
				#google_expire_time 설정
				if login_platform == 'naver' or login_platform == 'ical':
					if login_platform == 'naver':
						hostname = 'https://caldav.calendar.naver.com/principals/users/' + str(u_id)
					elif login_platform == 'ical':
						hostname = 'https://caldav.icloud.com/'

					#클라에서 loginState확인을 거쳐온 id/pw임으로 무조건 인증된 정보이다.
					client = CaldavClient(
					    hostname,
					    u_id,
					    u_pw
					)
					
					caldav_homeset = client.getPrincipal()
					homeset = principal.getHomeSet()
					caldav_homeset = homeset.homesetUrl			

					db_manager.query(
						"INSERT INTO USERACCOUNT " 
						"(account_hashkey,user_hashkey,login_platform,user_id,access_token,caldav_homeset)"
						"VALUES"
						"(%s, %s, %s, %s, %s, %s)",
						(			
							account_hashkey,
							user_hashkey,
							login_platform,
							u_id,
							u_pw,
							caldav_homeset
						)
					)

				elif login_platform =='google':

					db_manager.query(
							"INSERT INTO USERACCOUNT " 
							"(account_hashkey,user_hashkey,login_platform,user_id,access_token,google_expire_time)"
							"VALUES"
							"(%s, %s, %s, %s, %s, %s)",
							(			
								account_hashkey,
								user_hashkey,
								login_platform,
								u_id,
								access_token,
								google_expire_time
							)
						)
					

				db_manager.query(
					"INSERT INTO USERDEVICE " 
					"(device_hashkey,account_hashkey,session_key,push_token,device_type,app_version,device_info,uuid)"
					"VALUES"
					"(%s, %s, %s, %s, %s, %s, %s, %s)",
					(			
						device_hashkey,
						account_hashkey,
						session_key,
						push_token,
						device_type,
						app_version,
						device_info,
						uuid
					)
				)

				#세션관리를 위해 세션키를 키로 해시키로 매핑시킨다.
				#로그아웃시 해당 세션키를 보내서 날린다.
				redis.set(session_key,user_hashkey)
				return utils.resSuccess({'sessionkey':sessionkey})
			except Exception as e:
				return utils.resErr(str(e))		

		elif action == 'registerDevice':
			
			sessionkey = flask.request.form['sessionkey']
			# device_hashkey = utils.makeHashKey(account_hashkey)
			# session_key = utils.makeHashKey(device_hashkey)
			push_token = flask.request.form['pushToken']
			device_type = flask.request.form['deviceType']
			app_version = flask.request.form['appVersion']
			device_info = flask.request.form['deviceInfo']
			uuid = flask.request.form['uuid']
			

			try:

				#usder hashkey 를 받아내는 과정
				result = db_manager.query(
					"SELECT user_hashkey from USERDEVICE " +				
					"INNER JOIN USERACCOUNT on USERDEVICE.account_hashkey = USERACCOUNT.account_hashkey " +					
					"WHERE USERDEVICE.session_key = %s "
					,
					(									
						sessionkey,
					)
				)
				rows = utils.fetch_all_json(result)

				if len(rows) != 0:
					print('save redis hashkey '+str(rows[0]['user_hashkey']))
					redis.set(sessionkey,str(rows[0]['user_hashkey']))
				

				db_manager.query(
					"UPDATE USERDEVICE " +				
					"SET push_token = %s, " +
					"device_type = %s, " +
					"app_version = %s, " +
					"device_info = %s, " +
					"uuid = %s " +
					"WHERE session_key = %s "
					,
					(									
						push_token,
						device_type,
						app_version,
						device_info,
						uuid,
						sessionkey
					)
				)
				return utils.resSuccess({'sessionkey':sessionkey})
			except Exception as e:
				return utils.resErr(str(e))		

		elif action =='updatePushToken':
			push_token = flask.request.form['pushToken']
			sessionkey = flask.request.form['sessionkey']

			try:
				db_manager.query(
					"UPDATE USERDEVICE SET push_token = %s " 
					"WHERE session_key = %s "
					,
					(			
						push_token,
						sessionkey,						
					)
				)
				return utils.resSuccess('success')
			except Exception as e:
				return utils.resErr(str(e))		

			#로그아웃에선 레디스에서 해당 세션키를 날리고, is_active 를 false로
			#서버에서도 날려준다음
			#로그서버에 해당 사항을 저장해준다.
		elif action == 'logout':
			sessionkey = flask.request.form['sessionkey']
			try:
				db_manager.query(
					"UPDATE USERDEVICE " 
					"SET session_key = null, is_active = 0 "
					"WHERE session_key = %s",
					(									
						sessionkey,						
					)
				)	
				print('[redis]exist sessionkey result => '+ str(redis.get(sessionkey)))
				redis.delete(sessionkey)
				print('[redis]remvoe sessionkey! result=> '+str(redis.get(sessionkey)))
				
				return utils.resSuccess('logout success')
			except Exception as e:
				return utils.resErr(str(e))




			
