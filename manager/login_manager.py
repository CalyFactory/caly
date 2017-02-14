#-*- coding: utf-8 -*-
#author :yenos
#decript : 로그인 상태를 알려주는 매니저다. 
import json
from manager import db_manager
from common.util import utils
from common.util.statics import *
from caldavclient import CaldavClient
import base64

def checkLoginState(flask):
	
	sessionkey = flask.request.form['sessionkey']			
	login_platform = flask.request.form['loginPlatform']
	#세션키가 존재한다면 일반로그인이다.
	
	if sessionkey != 'null':
		print('null')
		result = db_manager.query(
				"SELECT * FROM USERDEVICE WHERE session_key = %s "
				,
				(sessionkey,) 						
		)
		rows = utils.fetch_all_json(result)
		if len(rows) != 0:
			return utils.loginState(LOGIN_STATE_AUTO,None)						
		else :
			return utils.loginState(LOGIN_ERROR_INVALID,None)			
	else:
		if login_platform == 'naver' or login_platform == 'ical':
			u_id = flask.request.form['uId']
			u_pw = flask.request.form['uPw']
			uuid = flask.request.form['uuid']
		
			if login_platform == 'naver':
				hostname = 'https://caldav.calendar.naver.com/principals/users/' + str(u_id)
			elif login_platform == 'ical':
				hostname = 'https://caldav.icloud.com/'

			client = CaldavClient(
			    hostname,
			    u_id,
			    u_pw
			)

			#FIXME!!! 
			#현재 로그인 실해일 경우 에러가 나서 유효하지않은 id/pw일것이다.
			#이를 에러가 아니라 특정 정보를 주어야한다. 400 msg 와 같이말이다.

			try:
				principal = client.getPrincipal()				
			except Exception as e:
				return utils.loginState(LOGIN_ERROR,'invalid id/pw')


			#id pw 에 맞는 유저가 있느니 검색하는 로직이다. 
			result = db_manager.query(
					"SELECT * FROM USERACCOUNT WHERE user_id = %s AND access_token = %s "
					,
					(u_id,u_pw) 						
			)
			rows = utils.fetch_all_json(result)	
			## 존재하지 않을경우 => 최초로그인
			if len(rows) == 0:
				isFirst = True
			### id pw 값이 존재할경우. => 로그아웃 이거나 다른 디바이스에서 로그인
			else :
				account_hashkey = rows[0]['account_hashkey']
				isFirst = False
			
			print('isFirst => '+str(isFirst))

			#세션키가 없는경우이면 최초 로그인 혹은  로그아웃 이다
			if sessionkey == 'null' :
				print('sessioneky none')

				result = db_manager.query(
						"SELECT * FROM USERDEVICE WHERE uuid = %s "
						,
						(uuid,) 						
				)
				rows = utils.fetch_all_json(result)

				#최초 회원가입인경우.
				#id/ow가 없다면 최초인경우다.
				if  isFirst == True:
					return utils.loginState(LOGIN_STATE_FIRST,None)
					# return LOGIN_STATE_FIRST
				
				#uuid가 db에 없고	id/pw가 있다면 새로운 기기에서의 등록이다.
				elif len(rows)== 0 and isFirst == False:					
					
					device_hashkey = utils.makeHashKey(account_hashkey)
					session_key = utils.makeHashKey(device_hashkey)

					db_manager.query(
						"INSERT INTO USERDEVICE " 
						"(device_hashkey,account_hashkey,session_key)"
						"VALUES"
						"(%s, %s, %s)",
						(			
							device_hashkey,
							account_hashkey,
							session_key
						)
					)					

					return utils.loginState(LOGIN_STATE_OTHERDEVICE,{'sessionkey':session_key})
					# return LOGIN_STATE_OTHERDEVICE

				#로그아웃인 경우.
				#uuid가 존재하고, id/;pw가 있다면 로그아웃 했던경우이다.
				# 새션키를 하나만들어서 넣어준다.

				elif len(rows)!=0 and isFirst == False:
					sessionkey = utils.makeHashKey(uuid)
					result = db_manager.query(
							"UPDATE USERDEVICE " +
							"SET session_key = %s " +
							"WHERE uuid = %s"
							,
							(sessionkey,uuid) 						
					)					
					return utils.loginState(LOGIN_STATE_RELOGIN,{'sessionkey':sessionkey})
					# return LOGIN_STATE_RELOGIN

