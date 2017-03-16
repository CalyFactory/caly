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

# from bot import slackAlarmBot
# slackAlarmBot.alertSyncEnd()


initRoute(app)
# if debugg
# logSet.init()

# if production
logging.basicConfig(level=logging.DEBUG, filename='log_caly.log',
                  format='%(asctime)s %(levelname)s: %(message)s',
                  datefmt='%Y-%m-%d %H:%M:%S')



@app.route('/')
def hello_wordl():
	return 'hello_world_other'

@app.route('/caldavTest')
def caldavTest():
	

	print('hi')
	# caldavWrapper.updateCal()
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
	

	# pks = "dtolwBZTUXk:APA91bH0WSHNkw8sF7syIMKKcyjmzpeUEh4NzsAenuaNPX36lOwezlz0_X7yVp8b2CUmFKoo1lJkKFXiEPcex9LgOj2RqV07Rdgxy17PEAOfDIMVblJC4Pss-HHGpf7v8WLsPIEUVXx-"
	# arr = ["cFK43rjMHoQ:APA91bE3HyJ1BVCI2Xrq3YJCrFll1Cjea3n8wVavHKiYVm1ktzRnbOrwICaSlBOcRP7Vg4c7fAFhBV4JdZd3fF-FZ49G8EgYgiozpKVAuXKU-3eI5YLleqghdBI521gvS4W_soc-vd4v","ejmnO9bSKDs:APA91bHyHu_W-jnnYWQqzEmvmlNarRZqJYEsC_6UHPCjpHmV0-0YrLA0-PXvfpYLarXg62qhZ6b_GFpg8yfqTL_fm8EEvM5PViF6mVbjSrSN4su9NwrY9bngzQSUMynJIB4LAIsSWzbl"]
	data_message = {
	    "type" : "noti",
	    "title" : "공지사항입니다 ",
	    "body" : "콩! 콩 콩진호가간다!"
	}
	# print(FCM.sendOnlyData(token,data_message))
	FCM.sendOnlyData(token,data_message)
	return 'FCM.sendOnlyData(token,data_message)'



if __name__ == '__main__':
	app.run(host='0.0.0.0', debug = True, port = 55566,threaded=True)

	
