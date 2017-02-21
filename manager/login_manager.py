#-*- coding: utf-8 -*-
#author :yenos
#decript : 로그인 상태를 알려주는 매니저다. 
import json

from manager import db_manager
from common.util import utils
from common.util.statics import *

from caldavclient import CaldavClient
from common import caldavWrapper
import base64
import datetime

from model import userDeviceModel
from model import userAccountModel
from model import userModel
from manager.redis import redis
def checkLoginState(flask):

	#세션키면 웹서버가 제공해주는 세션키라고 생각할수있다.
	#토큰이라든가로 처리해주는것이좋다.
	sessionkey = flask.request.form['sessionkey']


	#세션키가 존재한다면 일반로그인이다.
	#google / caldav 모두같음.	
	if sessionkey != 'null':
		print('sessionkey->'+sessionkey)
		
		# session['b85bb0921c6314aecccbed5701a2833f645a6b8ae3324a1723fca764'] = 'b6d41ddc29629e67ccc3fbed1e5a212811686c486c21bb3daf181cbf'
		# api에서 쓰는웹서버에서 쓰는 것을 사용하면안된다.
		# redis/memchached  
		# 서버 백앤드. 
		# 웹서버에서는 상태를 유지하기위한 스테이트풀 관리르 해준다. 
		# print('hash'+redis.get(sessionkey))		
		# codereview
		#세션키가 있다면.
		if redis.get(sessionkey):
			print('good')
			return utils.loginState(LOGIN_STATE_AUTO,None)		
		else:
			return utils.loginState(LOGIN_ERROR,None)				
		

	else:
		#없으면 에러처리를 해야한다.
		login_platform = flask.request.form['loginPlatform']
		uuid = flask.request.form['uuid']		
		#회원가입/로그아웃 재로그인/ 다른디바이스 로그인 경우이다.
		#캘데브일때는 캘데브 서버에서 인증확인을 받아야한다.
		if login_platform == 'naver' or login_platform == 'ical':
			
			u_id = flask.request.form['uId']
			u_pw = flask.request.form['uPw']
				
			calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)
			#FIXME!!! 
			#현재 로그인 실해일 경우 에러가 나서 유효하지않은 id/pw일것이다.
			#이를 에러가 아니라 특정 정보를 주어야한다. 400 msg 와 같이말이다.
			try:
				principal = calDavclient.getPrincipal()				
			except Exception as e:
				return utils.loginState(LOGIN_ERROR,'invalid id/pw')
			
			#cal dav일 경우.
			#id pw 에 맞는 유저가 있느니 검색하는 로직이다. 			
			try:
				#codeReview
				#id/pw가 
				#naver,ical이 같을경우 더많은 데이터가나올수있다.
				account = userAccountModel.getCaldavUserAccount(u_id,u_pw)
			except Exception as e:
				return utils.loginState(LOGIN_ERROR,str(e))
			#구글일경우
			#authCode값이 존재하고 해당 authcode로부터 subject를 추출한다.
			#
		elif login_platform == 'google':
			#id값으로 조회한다. 있는지 없는지.
			subject = flask.request.form['subject']
			#subject값이 있는지를 확인한다.
			#서브젝트가있는지판단.
			try:
				account = userAccountModel.getGoogleUserAccount(subject)
			except Exception as e:
				return utils.loginState(LOGIN_ERROR,str(e))
		
		## 존재하지 않을경우 => 최초로그인
		if len(account) == 0:
			isFirst = True
		
		### id pw 값 or subject에맞는 값이존재 => 로그아웃 이거나 다른 디바이스에서 로그인
		else :
			account_hashkey = account[0]['account_hashkey']
			isFirst = False
		
		print('isFirst => '+str(isFirst))

		#세션키가 없는경우이면 최초 로그인 혹은  로그아웃 이다
		if sessionkey == 'null' :

			try:
				#codereview
				#ros라 여러개나올것같다.
				device = userDeviceModel.getUserDeviceWithUuid(uuid)
			except Exception as e:
				return utils.loginState(LOGIN_ERROR,str(e))
			#최초 회원가입인경우.
			#id/pw or subject가 없다면 최초 회원가입인 경우이다.
			if  isFirst == True:
				
				#subject가 없는경우, 구글 최초 로그인
				return utils.loginState(LOGIN_STATE_FIRST,None)
					# return LOGIN_STATE_FIRST
				
				#uuid가 db에 없고	id/pw가 있다면 새로운 기기에서의 등록이다.
				#codeReview
				#isFirst 분기를 앞에서 함으로 여기서 체크할필요가없다.
			elif len(device)== 0 :					
				print('other device~!')
				device_hashkey = utils.makeHashKey(account_hashkey)
				session_key = utils.makeHashKey(device_hashkey)

				# updateSDK(flask)			

				try:
					userDeviceModel.setUserDevice(device_hashkey,account_hashkey,session_key)
				except Exception as e:
					return utils.loginState(LOGIN_ERROR,str(e))

				return utils.loginState(LOGIN_STATE_OTHERDEVICE,{'sessionkey':session_key})
				# return LOGIN_STATE_OTHERDEVICE

			#로그아웃인 경우.
			#uuid가 존재하고, id/;pw가 있다면 로그아웃 했던경우이다.
			# 새션키를 하나만들어서 넣어준다.

			elif len(device)!=0 :
				print('logout and return')
				sessionkey = utils.makeHashKey(uuid)
				user_hashkey = account[0]['user_hashkey']

				reids.set(sessionkey,account[0]['user_hashkey'])

				logging.debug('set sessionke =>'+ sessionkey)
				logging.debug('set userhashkey =>'+ account[0]['user_hashkey'])
				#codeReveiw
				#updateUserDeviceLogout 명확하지 않은 함수명.
				try:
					userDeviceModel.updateUserSession(sessionkey,uuid)
				except Exception as e:
					return utils.loginState(LOGIN_ERROR,str(e))

				return utils.loginState(LOGIN_STATE_RELOGIN,{'sessionkey':sessionkey})
				# return LOGIN_STATE_RELOGIN
#
#하위호환성 유지
#api경로따로짠다
#강제 업데이트를 한다.
# def updateSDK(flask):
# 	if 'sdkLevel' in flask.request.form:
# 		print('has sdk')
# 		sdkLevel = flask.request.form['sdkLevel']
		
# 		try:
# 			userDeviceModel.setSdkLevel(sessionkey,sdkLevel)
# 		except Exception as e:
# 			return utils.loginState(LOGIN_ERROR,str(e))					
