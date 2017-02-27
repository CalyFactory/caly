#-*- coding: utf-8 -*-
import json
import flask

import static
import uuid
import requests

from googleapiclient import discovery
from oauth2client import client
from manager import db_manager
from manager import network_manager
from datetime import datetime, timedelta


from juggernaut import Juggernaut

import urllib


from common.util import utils
from common import logSet

#route 안에 googleAuth파일로 들어가서 클래스인 GoogleAuth를 임포트하겠다.
from route.googleAuth import GoogleAuth
from route.schedule import Schedule

from route.routes import initRoute

from flask import render_template
from flask import redirect, url_for,session
from caldavclient import CaldavClient
from common import FCM
import logging
app = flask.Flask(__name__, static_url_path='')


initRoute(app)
logSet.init()

from datetime import datetime
from model import mFcmModel
logging.debug('currentServerTime=>'+str(datetime.now()))



##############
#  테스트요청	 #
##############
# @app.route('/testt')
# def testt():
# 	calendarModel.updateGoogleSyncState('1abfe3a73f9cfa147a6f962ef93ec414954c63bacc7ecd25632e6fa0',1)
# 	return 'hi'
# 	return utils.resCustom(
# 							210,
# 							{'msg':'MSG_INVALID_TOKENKEY'}
# 						)
# 	# return 'hi',402,{'Content-Type':'application/json'}
# 	# res = utils.multiReturn(200,'dataa','application/json')
# 	return utils.multiReturn(200,'dataa','application/json')

# @app.route('/refresh')
# def refresh():
# 	acToken = flask.request.args.get('acToken')

# 	from common import gAPI	
# 	#유효성 검사를 하고, 
# 	#유효하지 않으면 디비를 업데이트 한다. 
# 	# print(gAPI.checkValidAccessToken(acToken))


# 	print('ac=>'+acToken)
# 	validation_code = gAPI.checkValidAccessToken(acToken)
# 	logging.info('validCode = ==>'+str(validation_code))
# 	# if validation_code == 200 or validation_code == 201:
# 	# 	calendar_list_URL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
# 	# 	calendar_list = json.loads(network_manager.reqGET(calendar_list_URL,acToken))
		
# 	# 	1. 응답을 보내기전에 항상 validation check를 해야한다. 
# 	# 	2. 그리고 응답을 보낸후.code가 401일경우 다시 validation check를 한다.


# 	# 	logging.debug('data' + str(calendar_list['error']['code']))
# 	# 	logging.debug('data' + str(calendar_list))

# 	# 안되는
# 	# ya29.Glv5A5aE2I11yFYG6Q6LYKlfzF3h_dNVjpKf0R_wvKEe1AMeyma7E-lJo-Yx1bDIVaO5r2FoaGsHQ-zQl9OZz_jQw6f3JACUc555RXOkmCBldIxM5yzMyE8CZU1w
# 	# 에러가 존재한다면 다시 토큰을 요청한다.
# 	# if 'error' in calendar_list:


# 	# 	logging.info('noErr!!')
# 	# 	# refreshToken = '1/Xvx2_sr-AR0Rp9MCl7ToVltY9Xcf0v1u_9E7yw0W7z-kFF_DS7BDzafawYyFZGPW'
# 	# 	# refresh_info = gAPI.getRefreshAccessToken(refreshToken)
# 	# 	refresh_info = gAPI.checkValidAccessToken(acToken)
# 	# 	logging.info('refresh info ==>' + str(refresh_info))
# 	# 	if refresh_info:
# 	# 		new_access_token = refresh_info['access_token']

# 	# 		#accessToken update한다. 

# 	# 		return 'updated'
# 	# 	else:
# 	# 		return 'nope'

# 	return 'str(calendar_list)'

@app.route('/caldavTest')
def caldavTest():
	caldavWrapper.updateCal()
	return 'hi'

def event_stream():
    pubsub = redis.pubsub()
    pubsub.subscribe('syncAlert')
    for message in pubsub.listen():
        print (message)
        yield 'data: %s\n\n' % message['data']

def event_fetch_calendar():
	pubsub = redis.pubsub()
	pubsub.subscribe('fetchCalendar')
	for message in pubsub.listen():
		print (message)
		yield 'data: %s\n\n' % message['data']
#캘린더 리스트로 이동
@app.route('/calList')
def calList():
	return render_template('calList.html');			

#동기화 다된것 알리미
@app.route('/stream')
def stream():
    return flask.Response(event_stream(),
                          mimetype="text/event-stream")

@app.route('/fetchCalendar')
def fetchCalendar():
    return flask.Response(event_fetch_calendar(),
                          mimetype="text/event-stream")



#test Moudle
@app.route('/test_fetchFire')
def test_fetchFire():
	redis.publish('fetchCalendar', 'fetching!')
	return 'good' 

@app.route('/stopNoti')
def stopNoti():
	channel_id = flask.request.args.get('channel_id')		
	resource_id = flask.request.args.get('resource_id')		
	access_token = flask.request.args.get('access_token')		

	URL = 'https://www.googleapis.com/calendar/v3/channels/stop'
	body = {
		"id" : channel_id,
  		"resourceId": resource_id
	}	
	# print(network_manager.reqPOST(URL,body))
	return network_manager.reqPOST(URL,access_token,body) 
@app.route('/fireFcm')
def fireFcm():
	token = flask.request.args.get('token')		
	

	pks = "dtolwBZTUXk:APA91bH0WSHNkw8sF7syIMKKcyjmzpeUEh4NzsAenuaNPX36lOwezlz0_X7yVp8b2CUmFKoo1lJkKFXiEPcex9LgOj2RqV07Rdgxy17PEAOfDIMVblJC4Pss-HHGpf7v8WLsPIEUVXx-"
	arr = ["cFK43rjMHoQ:APA91bE3HyJ1BVCI2Xrq3YJCrFll1Cjea3n8wVavHKiYVm1ktzRnbOrwICaSlBOcRP7Vg4c7fAFhBV4JdZd3fF-FZ49G8EgYgiozpKVAuXKU-3eI5YLleqghdBI521gvS4W_soc-vd4v","ejmnO9bSKDs:APA91bHyHu_W-jnnYWQqzEmvmlNarRZqJYEsC_6UHPCjpHmV0-0YrLA0-PXvfpYLarXg62qhZ6b_GFpg8yfqTL_fm8EEvM5PViF6mVbjSrSN4su9NwrY9bngzQSUMynJIB4LAIsSWzbl"]
	data_message = {
	    "type" : "sync",
	    "action" : "actions"
	}
	print(FCM.sendOnlyData(token,data_message))
	return FCM.sendOnlyData(token,data_message)	





if __name__ == '__main__':

	ssl_context = ('./key/last.crt', './key/ssoma.key')
	app.run(host='0.0.0.0', debug = True, port = 55566, ssl_context = ssl_context,threaded=True)

	
