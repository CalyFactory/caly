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

from flask import redirect, url_for,session

from juggernaut import Juggernaut

import urllib


from common.util import utils
#route 안에 googleAuth파일로 들어가서 클래스인 GoogleAuth를 임포트하겠다.
from route.googleAuth import GoogleAuth
from route.schedule import Schedule

from route.routes import initRoute
from manager.redis import redis
from flask import render_template


app = flask.Flask(__name__, static_url_path='')

initRoute(app)
# print(utils.makeHashKey('test'))



##############
#  테스트요청	 #
##############

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
	URL = 'https://www.googleapis.com/calendar/v3/channels/stop'
	body = {
		"id" : channel_id,
  		"resourceId": resource_id
	}	
	# print(network_manager.reqPOST(URL,body))
	return network_manager.reqPOST(URL,body) 





if __name__ == '__main__':
	#session사용응ㄹ 위해선 secret_key가 존재해야한다.	
	# md5를 사용한다고합니다 uuid4
	app.secret_key = str(uuid.uuid4())	
	# app.permanent_session_lifetime = timedelta(seconds=3600)

	ssl_context = ('./key/last.crt', './key/ssoma.key')
	app.run(host='0.0.0.0', debug = True, port = 55566, ssl_context = ssl_context,threaded=True)

	
