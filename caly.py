#-*- coding: utf-8 -*-


import os
import json
import flask
os.environ["CALY_DB_CONF"] = "./key/conf.json"

import static
import uuid
import requests

from flask import render_template
from googleapiclient import discovery
from oauth2client import client
from manager import db_manager
from manager import network_manager
from datetime import datetime, timedelta


from juggernaut import Juggernaut

import urllib


from common.util import utils
from common import logSet
from common import gAPI

#route 안에 googleAuth파일로 들어가서 클래스인 GoogleAuth를 임포트하겠다.
from route.routes import initRoute

from flask import render_template
from flask import redirect, url_for,session
from caldavclient import CaldavClient
from common import FCM
import logging
import logging.handlers

app = flask.Flask(__name__, static_url_path='')
from common.flaskrun import flaskrun

initRoute(app)
# #-*- coding: utf-8 -*-
import logging
import logging.handlers


## 인스턴스만들기.
# mylogger = logging.getLogger()
# mylogger.setLevel(logging.INFO)
# rotatingHandler = logging.handlers.TimedRotatingFileHandler(filename='log/'+'log_caly.log', when='midnight', interval=1, encoding='utf-8')
# fomatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
# rotatingHandler.setFormatter(fomatter)
# mylogger.addHandler(rotatingHandler)


# if debugg
# logSet.init()


# # if production
logging.basicConfig(level=logging.INFO, filename='log/log_caly.log',
                  format='%(asctime)s %(levelname)s: %(message)s',
                  datefmt='%Y-%m-%d %H:%M:%S')

# from datetime import timedelta,datetime

# start_date = "2017-06-08 23:30:00+09:00"
# start_date = start_date[:start_date.find('+')]
# print(start_date)
# start_date = "1992-05-04"
# start_date = datetime.strptime(start_date, '%Y-%m-%d')
# # start_date = start_date + datetime.timedelta(hours=00,minutes=00)
# start_date = start_date.strftime('%Y-%m-%dT%H:%M:%S')

# print(start_date)
# from reco.reco import Reco
# from reinforce.reinforce import Reinforce
# import extractor.event_extractor  

# # extracted_json = extractor.event_extractor.extract_info_from_event('0024337293ce52d7f60a9e0532188b74865c42e8dbec644cfb333cee','선릉 민경이와 데이트','2017-06-13','2017-06-13','누우')
# logging.info("extrcted=>"+str(extracted_json))

# reinforce_json = Reinforce(extracted_json).event_reco_result
# logging.info("reinforce ->"+str(reinforce_json))


# reco = Reco(reinforce_json["event_info_data"])
# logging.info("recos==>"+str(reco.get_reco_list()))


# import logging
# import logging.handlers
# #인스턴스만들기.
# mylogger = logging.getLogger('MyLogger')
# mylogger.setLevel(logging.INFO)
# rotatingHandler = logging.handlers.TimedRotatingFileHandler(filename='log/'+ str(datetime.now())+'_log_caly.log', when='m', interval=3, encoding='utf-8')
# fomatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
# rotatingHandler.setFormatter(fomatter)
# mylogger.addHandler(rotatingHandler)
# logging = mylogger

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

@app.route('/testGoogleEvnets')
def testGoogleEvnets():

	calendar_id = flask.request.args.get('calendar_id')
	sync_token = flask.request.args.get('sync_token')		
	URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(calendar_id)+'/events'
	body = {
		'syncToken':sync_token
	}
	# access_token = 'ya29.GlthBLzu4Ont7fCiy9y-tz8bnrfwwbycBB1GfkBBZPw1dAWS5Ng36liEftgaDNgYNFJDHoGRZT-X1Adk75SspXSLpJkusY0zW7P0zVELMB9Ruc4PEBK-W_7SdTO_'
	# new_access_token = gAPI.checkValidAccessToken(access_token)	
	# logging.info('newacces=>'+ str(new_access_token))

	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + 'ya29.GlthBB5Js8pU404F_eoYnMzP20kDVverxK_L8cGhiDqQId12FvKsavw7iTN3vb-teIZOZu-R1KIn_ZMAwTwg8d_BoXFKAjCikfqAbkbZUcYfAzZP_MgkVvpPWl-u'		
	}	
	response = requests.get(URL,params = body,headers = headers)

	res = json.loads(response.text)				
	logging.info('new Res' + str(res))
	return 'hi'	

#test Moudle
@app.route('/test_fetchFire')
def test_fetchFire():
	redis.publish('fetchCalendar', 'fetching!')
	return 'good' 

@app.route('/stopNoti')
def stopNoti():
	channel_id = flask.request.args.get('channel_id')		
	resource_id = flask.request.args.get('resource_id')		
	# account_hashkey = flask.request.args.get('account_hashkey')		
	# ya29.GlsyBLU17MXx5UoOZAsbG3i2XDPSzQTaJKtPvQQ0w55C9EGEWV2Msk9zL45Wmcu5xHCON7fFdKNp6KsxaTUwPR6GVyCfvpEBsvR0bBD-eiyyjpKkIAySurthCXmh
	access_token = flask.request.args.get('access_token')		

	URL = 'https://www.googleapis.com/calendar/v3/channels/stop'
	body = {
		"id" : channel_id,
  		"resourceId": resource_id
	}	
	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + access_token
	}
	return requests.post(URL,data = json.dumps(body),headers = headers).text
	
@app.route('/fireFcm')
def fireFcm():
	token = flask.request.args.get('token')		
	
	data_message = {
	    "type" : "noti",
	    "title" : "공지사항입니다 ",
	    "body" : "콩! 콩 콩진호가간다!"
	}
	result = FCM.sendOnlyData(token,data_message)
	logging.info(str(result))
	return 'FCM.sendOnlyData(token,data_message)'

@app.route("/privacyPolicy", methods = ["GET"])
def page_login_get():
    
    return render_template('privacyPolicy.html')

if __name__ == '__main__':
	flaskrun(app)



	
