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
from common import cryptoo

def checkLoginState(flask):

	#세션키면 웹서버가 제공해주는 세션키라고 생각할수있다.
	#토큰이라든가로 처리해주는것이좋다.
	apikey = flask.request.form['apikey']


	#세션키가 존재한다면 일반로그인이다.
	#google / caldav 모두같음.	
	if apikey != 'null':
		logging.info('apikey!!->'+apikey)
		
		
		if redis.get(apikey):

			#유저라이프사이클로그저장.
			statee.userLife(apikey,LIFE_STATE_SIGNIN_AUTO)									
			try:
				logging.info('activs->')
				activs = userAccountModel.getIsActive(apikey)

				if activs[0]['is_active'] == 3:
					return utils.loginState(LOGIN_STATE_CHANGEPW,None)			
				try:
					
					user = userAccountModel.getUserAccountWithApikey(apikey)	
					logging.info('userss->'+str(user))

					userAccountModel.updateIsActiveWithUserHasheky(user[0]['user_hashkey'],1)
				except Exception as e:
					logging.error(str(e))

				return utils.loginState(LOGIN_STATE_AUTO,None)		
			except Exception as e:
				return utils.loginState(LOGIN_ERROR,None)

		else:	
			return utils.loginState(LOGIN_ERROR,None)				
		

	else:
		#없으면 에러처리를 해야한다.
		login_platform = flask.request.form['loginPlatform']
		uuid = flask.request.form['uuid']		
		#회원가입/로그아웃 재로그인/ 다른디바이스 로그인 경우이다.
		#캘데브일때는 캘데브 서버에서 인증확인을 받아야한다.
		if login_platform == 'naver' or login_platform == 'ical':
			logging.info('naver')
			u_id = flask.request.form['uId']
			u_pw = flask.request.form['uPw']
			u_pw = cryptoo.encryptt(u_pw)	
			calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)
			#FIXME!!! 
			#현재 로그인 실해일 경우 에러가 나서 유효하지않은 id/pw일것이다.
			#이를 에러가 아니라 특정 정보를 주어야한다. 400 msg 와 같이말이다.
			try:
				principal = calDavclient.getPrincipal()				
			except Exception as e:			
				logging.error(str(e))			
				return utils.loginState(LOGIN_ERROR_INVALID,None)
			
			#cal dav일 경우.
			#id pw 에 맞는 유저가 있느니 검색하는 로직이다. 			
			try:
				#codeReview
				#id/pw가 
				#naver,ical이 같을경우 더많은 데이터가나올수있다.
				account = userAccountModel.getCaldavUserAccount(u_id,login_platform)
			except Exception as e:
				logging.error(str(e))
				return utils.loginState(LOGIN_ERROR,str(e))
			#구글일경우
			#authCode값이 존재하고 해당 authcode로부터 subject를 추출한다.
			#
		elif login_platform == 'google':
			logging.info('google')
			#id값으로 조회한다. 있는지 없는지.
			subject = flask.request.form['subject']
			#subject값이 있는지를 확인한다.
			#서브젝트가있는지판단.
			try:
				account = userAccountModel.getGoogleUserAccount(subject)
			except Exception as e:
				logging.error(str(e))
				return utils.loginState(LOGIN_ERROR,str(e))
		
		## 존재하지 않을경우 => 최초로그인
		if len(account) == 0:
			isFirst = True		
		### id pw 값 or subject에맞는 값이존재 => 로그아웃 이거나 다른 디바이스에서 로그인
		else :
			account_hashkey = account[0]['account_hashkey']
			user_hashkey = account[0]['user_hashkey']
			user_is_active = userModel.getUserIsActive(user_hashkey)[0]['is_active']
			isFirst = False
		
		logging.info('isFirst => '+str(isFirst))

		#세션키가 없는경우이면 최초 로그인 혹은  로그아웃 이다
		if apikey == 'null' :

			#앱내부에서 계정추가를 하여 데이터가 이미 개인개정이 존재할경우 아래로직을 타게된다
			if  isFirst == False:

				try:

					#codereview
					#디바이스가 존재하는지확인.
					device = userDeviceModel.getUserDeviceWithUuid(uuid)
					##통합로그인
					#해당 어카운트해시키를 가지는지 확인
					deviceHasAccount = userDeviceModel.getUserDeviceWithAccountHashkey(account_hashkey)
					logging.info('device has account = '+str(user_hashkey))
					hasAccountInDevices = True
					#해당 유저 어카운트가 존재하는지 확인
					logging.info('device has account = '+str(deviceHasAccount))
					#0일경우
					if len(deviceHasAccount) == 0:					
						hasAccountInDevices = False


				except Exception as e:
					logging.error(str(e))
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
	
					try:
						user = userAccountModel.getUserAccountWithApikey(apikey)				
						userAccountModel.updateIsActiveWithUserHasheky(user[0]['user_hashkey'],1)
					except Exception as e:
						logging.info(str(e))


				except Exception as e:
					logging.error(str(e))
					return utils.loginState(LOGIN_ERROR,str(e))


				return utils.loginState(LOGIN_STATE_RESIGNUP,{'apikey':apikey})

#디바이스가 없으면 완전 새로운 디바이스 로그인
			elif len(device) == 0 :					
				logging.info('other device~!')
				device_hashkey = utils.makeHashKey(account_hashkey)
				apikey = utils.makeHashKey(device_hashkey)

				
				try:
					userDeviceModel.setUserDevice(device_hashkey,account_hashkey,apikey)
					redis.set(apikey,user_hashkey)
				except Exception as e:
					logging.error(str(e))
					return utils.loginState(LOGIN_ERROR,str(e))
				
				statee.userLife(apikey,LIFE_STATE_SIGNIN_OTEHRDEVICE)	

				try:
					user = userAccountModel.getUserAccountWithApikey(apikey)				
					userAccountModel.updateIsActiveWithUserHasheky(user[0]['user_hashkey'],1)
				except Exception as e:
					logging.info(str(e))				
					
				return utils.loginState(LOGIN_STATE_OTHERDEVICE,{'apikey':apikey})
				# return LOGIN_STATE_OTHERDEVICE

			#로그아웃인 경우.
			#uuid가 존재하고, id/;pw가 있다면 로그아웃 했던경우이다.
			# 새션키를 하나만들어서 넣어준다.
			# 디바이스가 존재하면 다른 유저가 가입했거나, 로그아웃 해서 다시들어옴
			elif len(device)!=0 :
				logging.info('logout and return ')
				apikey = utils.makeHashKey(uuid)

				redis.set(apikey,user_hashkey)

				logging.info('set apikey =>'+ apikey)
				logging.info('set userhashkey =>'+ user_hashkey)
				logging.info('set account_hashkey =>'+ account_hashkey)
				#codeReveiw
				#updateUserDeviceLogout 명확하지 않은 함수명.
				try:

					#최초 로그인계정과 다른 연동된계정으로 로그인
					#최초 kkk 추가 vudrkd
					#로그아웃후 vudrkd으로 로그인할 경우
					#만약 userAccount가 존재하지않는다면
					#현재 hashAccount로 바꿔줘야한다. 기존uuid있는것을
					if hasAccountInDevices == False:
						logging.info('!!!login another ACCOUNT !!!!')
						userDeviceModel.updateAccountHashkey(account_hashkey,uuid,apikey)
						statee.userLife(apikey,LIFE_STATE_SIGNIN_RELOGIN_OTHERACCOUNT)
					#일반 로그인
					#kkk로 로그인 했을경우
					#userAccount가 존재한다면 기존것에 그냥 업데이트시켜주면됨
					else:
						logging.info('!!!login exsiting ACCOUNT !!!!')
						userDeviceModel.updateUserApikeyWihtUuid(account_hashkey,uuid,apikey)
						statee.userLife(apikey,LIFE_STATE_SIGNIN_RELOGIN)
	
					try:
						user = userAccountModel.getUserAccountWithApikey(apikey)				
						userAccountModel.updateIsActiveWithUserHasheky(user[0]['user_hashkey'],1)
					except Exception as e:
						logging.info(str(e))
	
					
				except Exception as e:
					logging.error(str(e))
					return utils.loginState(LOGIN_ERROR,str(e))
				
																							
			
				return utils.loginState(LOGIN_STATE_RELOGIN,{'apikey':apikey})

