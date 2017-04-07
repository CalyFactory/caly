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
from route.routes import initRoute

from flask import render_template
from flask import redirect, url_for,session
from caldavclient import CaldavClient
from common import FCM
import logging
app = flask.Flask(__name__, static_url_path='')
from common.flaskrun import flaskrun

initRoute(app)
# if debugg
# logSet.init()

# if production
logging.basicConfig(level=logging.INFO, filename='log/log_caly.log',
                  format='%(asctime)s %(levelname)s: %(message)s',
                  datefmt='%Y-%m-%d %H:%M:%S')

@app.route('/')
def hello_wordl():
	return 'hello_world_other'

@app.route('/caldavTest')
def caldavTest():
	return 'hi'

def event_stream():
    pubsub = redis.pubsub()
    pubsub.subscribe('syncAlert')
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']

def event_fetch_calendar():
	pubsub = redis.pubsub()
	pubsub.subscribe('fetchCalendar')
	for message in pubsub.listen():
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
	return network_manager.reqPOST(URL,access_token,body) 
	
@app.route('/fireFcm')
def fireFcm():
	token = flask.request.args.get('token')		
	
	data_message = {
	    "type" : "noti",
	    "title" : "공지사항입니다 ",
	    "body" : "콩! 콩 콩진호가간다!"
	}
	FCM.sendOnlyData(token,data_message)
	return 'FCM.sendOnlyData(token,data_message)'

if __name__ == '__main__':
	flaskrun(app)



	
