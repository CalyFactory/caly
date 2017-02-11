#-*- coding: utf-8 -*-
from flask.views import MethodView
from common.util import utils
from manager import db_manager
import flask
from common.util import utils
# yenos
# 유저의관한 api 리스트이다.
class Member(MethodView):

	def post(self,action):
		if action == 'loginCheck':
			#TODO
			#앱 버전을 꾸준히 체크해줘야한다.
			#app_version = flask.request.form['app_version']
			
			
			sessionkey = flask.request.form['sessionkey']			

			#세션키가 존재한다면 일반로그인이다.
			if sessionkey != 'null':			
				try:
					result = db_manager.query(
							"SELECT * FROM USERDEVICE WHERE session_key = %s "
							,
							(sessionkey,) 						
					)
					rows = utils.fetch_all_json(result)
					if len(rows) != 0:
						return utils.resSuccess('auto login success')						
					else :
						return utils.reserr('inValid sessionKey')						

				except Exception as e:
					return utils.resErr(str(e))							

			#최초 회원가입할 경우.
			# 새로운 기기에서 등록하였을 경우.
			# 같은 디바이스에서 로그아웃하여 다시 접속하려고하는 경우.
			else:

				u_id = flask.request.form['uId']
				u_pw = flask.request.form['uPw']
				uuid = flask.request.form['uuid']

				#id pw 에 맞는 유저가 있느니 검색하는 로직이다. 
				try:
					result = db_manager.query(
							"SELECT * FROM USERACCOUNT WHERE user_id = %s AND access_token = %s "
							,
							(u_id,u_pw) 						
					)
					rows = utils.fetch_all_json(result)
				except Exception as e:
					return utils.resErr(str(e))				
				## 존재하지 않을경우 => 최초로그인
				if len(rows) == 0:
					isFirst = True
				### id pw 값이 존재할경우. => 로그아웃 이거나 다른 디바이스에서 로그인
				else :
					account_hashkey = rows[0]['account_hashkey']
					isFirst = False
				
				print('isFirst => '+str(isFirst))

				#세션키가 없는경우이면 최초 로그인  로그아웃 이다
				if sessionkey == 'null' :
					print('sessioneky none')
					try:
						result = db_manager.query(
								"SELECT * FROM USERDEVICE WHERE uuid = %s "
								,
								(uuid,) 						
						)
						rows = utils.fetch_all_json(result)
					except Exception as e:
						return utils.resErr(str(e))
					#최초 회원가입인경우.
					#id/ow가 없다면 최초인경우다.
					if  isFirst == True:
						return utils.resCustom(201,'first sign up')
					
					#uuid가 db에 없고	id/pw가 있다면 새로운 기기에서의 등록이다.
					elif len(rows)== 0 and isFirst == False:

						return utils.resCustom(207,{'account_hashkey':account_hashkey})	

					#로그아웃인 경우.
					#uuid가 존재하고, id/;pw가 있다면 로그아웃 했던경우이다.
					# 혹은 
					elif len(rows)!=0 and isFirst == False:
						return utils.resCustom(205,'u will logout')

			
		elif action == 'signUp':
			print('signup')
			u_id = flask.request.form['uId']
			u_pw = flask.request.form['uPw']
			#1남자 2여자
			gender = flask.request.form['gender']
			birth = flask.request.form['birth']
			login_platform = flask.request.form['loginPlatform']
			#TODO
			#caldav_homeset = flask.request.form['caldavHomeset']
			#googleExpireTime = flask.request.form['googleExpireTime']

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
				db_manager.query(
					"INSERT INTO USERACCOUNT " 
					"(account_hashkey,user_hashkey,login_platform,user_id,access_token)"
					"VALUES"
					"(%s, %s, %s, %s, %s)",
					(			
						account_hashkey,
						user_hashkey,
						login_platform,
						u_id,
						u_pw
					)
				)

				#TODO
				#calendar HomeSat
				#google_expire_time 설정
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
				return utils.resSuccess({'sessionkey':sessionkey})
			except Exception as e:
				return utils.resErr(str(e))		
		elif action == 'registerDevice':
			
			account_hashkey = flask.request.form['accountHasheky']
			device_hashkey = utils.makeHashKey(account_hashkey)
			session_key = utils.makeHashKey(device_hashkey)
			push_token = flask.request.form['pushToken']
			device_type = flask.request.form['deviceType']
			app_version = flask.request.form['appVersion']
			device_info = flask.request.form['deviceInfo']
			uuid = flask.request.form['uuid']

			try:
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
				return utils.resSuccess({'sessionkey':session_key})
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




			
