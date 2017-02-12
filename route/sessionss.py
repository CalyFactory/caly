from manager import db_manager
from common.util import utils
from common.util.statics import *
# LOGIN_STATE_FIRST = 'LOGIN_STATS_SIGNUP'
# LOGIN_STATE_AUTO = 'LOGIN_STATE_AUTO'
# LOGIN_STATE_OTHERDEVICE = 'LOGIN_STATE_OTHERDEVICE'
# LOGIN_STATE_RELOGIN = 'LOGIN_STATE_RELOGIN'
def checkLoginState(sessionkey,platform):

	#세션키가 존재한다면 일반로그인이다.
	if sessionkey != 'null':
		
		result = db_manager.query(
				"SELECT * FROM USERDEVICE WHERE session_key = %s "
				,
				(sessionkey,) 						
		)
		rows = utils.fetch_all_json(result)
		if len(rows) != 0:
			return LOGIN_STATE_AUTO						
		else :
			return LOGIN_ERROR_INVALID
	else:
		if platform == 'caldav':
			u_id = flask.request.form['uId']
			u_pw = flask.request.form['uPw']
			uuid = flask.request.form['uuid']

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

			#세션키가 없는경우이면 최초 로그인  로그아웃 이다
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
					return LOGIN_STATE_FIRST
				
				#uuid가 db에 없고	id/pw가 있다면 새로운 기기에서의 등록이다.
				elif len(rows)== 0 and isFirst == False:

					return LOGIN_STATE_OTHERDEVICE

				#로그아웃인 경우.
				#uuid가 존재하고, id/;pw가 있다면 로그아웃 했던경우이다.
				# 혹은 
				elif len(rows)!=0 and isFirst == False:
					return LOGIN_STATE_RELOGIN

