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
import logging
from common import statee

def checkLoginState(flask):

	#세션키면 웹서버가 제공해주는 세션키라고 생각할수있다.
	#토큰이라든가로 처리해주는것이좋다.
	apikey = flask.request.form['apikey']


	#세션키가 존재한다면 일반로그인이다.
	#google / caldav 모두같음.	
	if apikey != 'null':
		logging.debug('apikey->'+apikey)
		
		
		if redis.get(apikey):

			#유저라이프사이클로그저장.
			statee.userLife(apikey,LIFE_STATE_SIGNIN_AUTO)									
			
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
			logging.debug('naver')
			u_id = flask.request.form['uId']
			u_pw = flask.request.form['uPw']
				
			calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)
			#FIXME!!! 
			#현재 로그인 실해일 경우 에러가 나서 유효하지않은 id/pw일것이다.
			#이를 에러가 아니라 특정 정보를 주어야한다. 400 msg 와 같이말이다.
			try:
				principal = calDavclient.getPrincipal()				
			except Exception as e:						
				return utils.loginState(LOGIN_ERROR_INVALID,'invalid id/pw')
			
			#cal dav일 경우.
			#id pw 에 맞는 유저가 있느니 검색하는 로직이다. 			
			try:
				#codeReview
				#id/pw가 
				#naver,ical이 같을경우 더많은 데이터가나올수있다.
				account = userAccountModel.getCaldavUserAccount(u_id,u_pw,login_platform)
			except Exception as e:
				return utils.loginState(LOGIN_ERROR,str(e))
			#구글일경우
			#authCode값이 존재하고 해당 authcode로부터 subject를 추출한다.
			#
		elif login_platform == 'google':
			logging.debug('google')
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
			user_hashkey = account[0]['user_hashkey']
			isFirst = False
		
		logging.debug('isFirst => '+str(isFirst))

		#세션키가 없는경우이면 최초 로그인 혹은  로그아웃 이다
		if apikey == 'null' :

			try:
				#codereview
				#ros라 여러개나올것같다.
				device = userDeviceModel.getUserDeviceWithUuid(uuid)
				user_is_active = userModel.getUserIsActive(user_hashkey)[0]['is_active']

			except Exception as e:
				return utils.loginState(LOGIN_ERROR,str(e))
			#최초 회원가입인경우.
			#id/pw or subject가 없다면 최초 회원가입인 경우이다.
			if  isFirst == True:
				
				#subject가 없는경우, 구글 최초 로그인
				return utils.loginState(LOGIN_STATE_FIRST,None)
					# return LOGIN_STATE_FIRST
				
				#uuid가 db에 없고	id/pw가 있다면 새로운 기기에서의 등록이다.
			
			#user is_active 가 0 일경우 탈퇴한 유저가 다시 가입하는 경우다.
			elif user_is_active == 0 :
				apikey = utils.makeHashKey(user_hashkey)
				device_hashkey = utils.makeHashKey(account_hashkey)				
				try:

					userDeviceModel.setUserDevice(device_hashkey,account_hashkey,apikey)
					redis.set(apikey,user_hashkey)
				except Exception as e:
					return utils.loginState(LOGIN_ERROR,str(e))


				return utils.loginState(LOGIN_STATE_RESIGNUP,{'apikey':apikey})

			elif len(device) == 0 :					
				logging.debug('other device~!')
				device_hashkey = utils.makeHashKey(account_hashkey)
				apikey = utils.makeHashKey(device_hashkey)

				
				try:
					userDeviceModel.setUserDevice(device_hashkey,account_hashkey,apikey)
					redis.set(apikey,user_hashkey)
				except Exception as e:
					return utils.loginState(LOGIN_ERROR,str(e))
				
				statee.userLife(apikey,LIFE_STATE_SIGNIN_OTEHRDEVICE)														
				
				return utils.loginState(LOGIN_STATE_OTHERDEVICE,{'apikey':apikey})
				# return LOGIN_STATE_OTHERDEVICE

			#로그아웃인 경우.
			#uuid가 존재하고, id/;pw가 있다면 로그아웃 했던경우이다.
			# 새션키를 하나만들어서 넣어준다.

			elif len(device)!=0 :
				logging.debug('logout and return')
				apikey = utils.makeHashKey(uuid)

				redis.set(apikey,user_hashkey)

				logging.debug('set apikey =>'+ apikey)
				logging.debug('set userhashkey =>'+ user_hashkey)
				#codeReveiw
				#updateUserDeviceLogout 명확하지 않은 함수명.
				try:
					userDeviceModel.updateUserApikey(apikey,uuid)
				except Exception as e:
					return utils.loginState(LOGIN_ERROR,str(e))
				
				statee.userLife(apikey,LIFE_STATE_SIGNIN_RELOGIN)																			
			
				return utils.loginState(LOGIN_STATE_RELOGIN,{'apikey':apikey})

