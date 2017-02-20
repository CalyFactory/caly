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

app = flask.Flask(__name__, static_url_path='')


initRoute(app)
logSet.init()

##############
#  테스트요청	 #
##############
# from common import caldavWrapper
import logging
@app.route('/refresh')
def refresh():
	acToken = flask.request.args.get('acToken')
	calendar_list_URL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
	calendar_list = json.loads(network_manager.reqGET(calendar_list_URL,acToken))
	
	logging.debug('calendarList=>' + str(calendar_list))
	from common import gAPI
	#에러가 존재한다면 다시 토큰을 요청한다.
	if 'error' in calendar_list:
		refreshToken = '1/Xvx2_sr-AR0Rp9MCl7ToVltY9Xcf0v1u_9E7yw0W7z-kFF_DS7BDzafawYyFZGPW'
		return gAPI.getRefreshAccessToken(refreshToken)
		# logging.debug('error! request reToken')
		# return gAPI.getOauthCredentials(refreshToken)

	return str(calendar_list)

# @app.route('/testOauth')
# def testOauth():
# 	from common import gAPI
# 	authCode = flask.request.args.get('authCode')
# 	return str(gAPI.getOauthCredentials(authCode))

    # from oauth2client.client import OAuth2WebServerFlow
    # from oauth2client.tools import run_flow
    # from oauth2client.file import Storage
    # authCode = flask.request.args.get('authCode')
    # CLIENT_ID = '<client_id>'
    # CLIENT_SECRET = '<client_secret>'
    # flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
	   #                      client_secret=CLIENT_SECRET,
				# 		    scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.readonly',
				# 		    redirect_uri='https://ssoma.xyz:55566/googleAuthCallBack',
    #         	            prompt='consent')
    # storage = Storage('creds.data')
    # credentials = run_flow(flow, storage)
    # logging.info(str(credentials))
    # print "access_token: %s" % credentials.access_token



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

	
