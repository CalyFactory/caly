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
from manager.redis import redis

from flask import render_template

app = flask.Flask(__name__, static_url_path='')


#googleOauth라우팅
googleAuth = GoogleAuth.as_view('gAuthAPI')
app.add_url_rule(
					'/', 
					defaults={'action': 'index'},
	                view_func=googleAuth, 
	                methods=['GET', ]
                )


app.add_url_rule(
					'/googleAuthCallBack', 
					defaults={'action': 'googleAuthCallBack'},
                 	view_func=googleAuth, 
                 	methods=['GET', ]
                 )

app.add_url_rule(
					'/calendarSync', 
					defaults={'action': 'calendarSync'},
                 	view_func=googleAuth, 
                 	methods=['GET', ]
                 )
app.add_url_rule(
					'/googleReceive', 
					defaults={'action': 'googleReceive'},
                 	view_func=googleAuth, 
                 	methods=['POST', ]
                 )

#schedule라우팅
schedule = Schedule.as_view('schedule')
app.add_url_rule(
					'/getCalendarList',
					defaults = {'action':'getCalendarList'},
					view_func = schedule,
					methods=['GET',]
				)
app.add_url_rule(
					'/setCalendarList',
					defaults = {'action':'setCalendarList'},
					view_func = schedule,
					methods=['GET',]
				)
app.add_url_rule(
					'/getEvents',
					defaults = {'action':'getEvents'},
					view_func = schedule,
					methods=['GET',]
				)




# @app.route('/')
# def index():		
# 	return flask.redirect(flask.url_for('googleAuthCallBack'))

# @app.route('/googleAuthCallBack')
# def googleAuthCallBack():
# 	#유저 권한을 요구한다.
# 	#client_secret으로 서버를 확인한다. 
# 	flow = client.flow_from_clientsecrets(
# 	'client_secret.json',
# 	scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.readonly',
# 	redirect_uri=flask.url_for('googleAuthCallBack', _external=True))
# 	#위코드는아래와같다
# 	#Google은 사용자 인증 및 동의를 처리한 후 인증 코드를 반환합니다. 
# 	#애플리케이션은 액세스 토큰을 받기 위해 client_id 및 client_secret과 함께 인증 코드를 사용하며, 이 인증 코드는 사용자를 대신하여 API 요청을 인증하는 데 사용될 수 있습니다. 이 단계에서 애플리케이션은 이전에 받은 토큰이 만료될 경우 애플리케이션이 새 액세스 토큰을 받을 수 있게 해주는 갱신 토큰을 요청할 수도 있습니다.
# 	if 'code' not in flask.request.args:
# 		#구글로부터 url을 요청한다.
# 		auth_uri = flow.step1_get_authorize_url()
# 		return flask.redirect(auth_uri)		
# 	else:
# 		auth_code = flask.request.args.get('code')
# 		#유저정보를 받아온다.
# 		credentials = json.loads(flow.step2_exchange(auth_code).to_json())
# 		print(credentials)
# 		print(credentials['access_token'])
# 		print(credentials['id_token']['email'])

# 		redis.set('access_token',credentials['access_token'])
# 		redis.set('mail',credentials['id_token']['email'])
# 		# flask.session['access_token'] = credentials['access_token']
# 		# flask.session['mail'] = credentials['id_token']['email']
		
# 		result = db_manager.query(
# 			"SELECT * FROM user WHERE mail = %s",(credentials['id_token']['email'],)
# 		)
# 		rows = utils.fetch_all_json(result)
		
# 		#조회결과 없다면!디비에 넣는다. 
# 		if len(rows) == 0:
# 			db_manager.query(
# 				"INSERT INTO user " 
# 				"(`mail`, `access_token`)"
# 				"VALUES"
# 				"(%s, %s)",
# 				(			
# 					credentials['id_token']['email'],
# 					credentials['access_token']
# 				)
# 			)			
# 		return flask.redirect(flask.url_for('calendarSync'))

# @app.route('/calendarSync')
# def calendarSync():
# 	print('session user token => '+ redis.get('access_token'))
	
# 	# calendarListURL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
# 	# calendarList = json.loads(reqGET(calendarListURL))
# 	# print (calendarList['items'])
# 	return redirect(url_for('static', filename='syncList.html'))

#web에서 캘린더리스트를 불러오도록한다.
# @app.route('/getCalendarList')
# def getCalendarList():

# 	calendarListURL = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
# 	calendarList = json.loads(reqGET(calendarListURL))
# 	returnValue = {}
# 	dataArray = []
# 	data = {}

# 	returnValue['userId'] = redis.get('mail');

# 	for item in calendarList['items']:
# 		data = {}
# 		data['id'] = item['id']
# 		data['name'] = item['summary']
# 		dataArray.append(data)

# 	returnValue['data'] = dataArray

# 	return json.dumps(returnValue)

#web에서 캘린더리스트를 클릭하도록한다.
# @app.route('/setCalendarList')
# def setCalendarList():

# 	dataArray = flask.request.args.get('data')
# 	userId = flask.request.args.get('userId')	
# 	alreadySyncCnt = 0;
# 	print(dataArray)
# 	# calendarData = ""	
# 	# 	calendarData += "("+item['id']+","+userId+"),"
# 	# calendarData = calendarData[:-1]	
# 	try:
# 		for item in json.loads(dataArray):
# 			channelId = str(uuid.uuid4())
# 			print('channelid '+channelId)
			
# 			result = db_manager.query(
# 					"SELECT * FROM calendarList WHERE calendar_id = %s",([item['id']])
# 				)
# 			rows = utils.fetch_all_json(result)

# 			#길이가 0 이면 아예 등록되지않은상태.
# 			if len(rows) == 0: 
# 				db_manager.query(
# 							"INSERT INTO calendarList " 
# 							"(`calendar_id`, `mail`,`channel_id`)"
# 							"VALUES"
# 							"(%s, %s,%s)",
# 							(			
# 								item['id'],userId,channelId
# 							)
# 						)			
# 				URL = 'https://www.googleapis.com/calendar/v3/calendars/'+item['id']+'/events/watch'
# 				body = {
# 					"id" : channelId,
# 					"type" : "web_hook",
# 					"address" : "https://ssoma.xyz:55566/googleReceive"
# 				}
# 				network_manager.reqPOST(URL,body)
# 			else:
# 				alreadySyncCnt += 1				
# 		if alreadySyncCnt > 0:
# 			redis.publish('chat', 'already sync!')

# 	except Exception as e:
# 		print("erorr => "+str(e))

# 	return 'good'	

	
# def reqPOST(URL,body = {}):
# 	#여기서 Authorization Bearer 뒤에 값은 유저 액세스 토큰이다.
# 	headers = {
# 		'content-Type': 'application/json',
# 		'Authorization' : 'Bearer ' + redis.get('access_token')
# 	}
# 	response = requests.post(URL,data = json.dumps(body),headers = headers)
# 	return response.text

# def reqGET(URL,params = {}):
# 	headers = {
# 		'content-Type': 'application/json',
# 		'Authorization' : 'Bearer ' + redis.get('access_token')
		
# 	}	
# 	response = requests.get(URL,params = params,headers = headers)
# 	return response.text

# @app.route('/googleReceive',methods = ['POST'])
# def googleReceive():
# 	print("receiveGooge")

# 	print(flask.request.headers)
# 	print(flask.request.headers['X-Goog-Channel-Id'])
# 	channelId = flask.request.headers['X-Goog-Channel-Id']

# 	result = db_manager.query(
# 			"SELECT * FROM calendarList WHERE channel_id = %s",(channelId,)
# 		)
# 	rows = utils.fetch_all_json(result)
	
# 	#channelId 같은게 있다면 isRegitPush를 1로 만들어준다.
# 	#이것은 푸시등록이 완벽히 됬음을 의미한다.
# 	if len(rows) != 0 and rows[0]['isRegitPush'] == 0 :
# 		result = db_manager.query(
# 			"UPDATE calendarList SET isRegitPush = 1 WHERE channel_id = %s"
# 			,(channelId,)
# 		)
# 		setEvents(rows[0]['mail'])
# 		redis.publish('chat', 'sync Success')
# 	else:
# 		print("else")
	
# 	return 'json.dumps(files)'	



# def setEvents(mail):
# 	# mail = flask.request.args.get('mail')		
# 	# print('setAlleventsCall')
# 	result = db_manager.query(
# 			"SELECT * FROM calendarList WHERE mail = %s",(mail,)
# 		)
# 	rows = utils.fetch_all_json(result)
	
# 	for row in rows:	
# 		URL = 'https://www.googleapis.com/calendar/v3/calendars/'+urllib.request.pathname2url(str(row['calendar_id']))+'/events'
# 		print('url =>'+URL)
# 		res = json.loads(network_manager.reqGET(URL))
# 		# print('calender_id=>'+row['calendar_id'])
# 		# print('ressss=>'+str(res))
# 		# print('res=> ' + str(res['summary']))		
# 		calendar_id = row['calendar_id']
# 		syncToken = res['nextSyncToken']

# 		for item in res['items']:
# 			print('event_id=>'+str(item['id']))

# 			event_id = item['id']
# 			summary = 'noTitle'
# 			start_date = None
# 			end_date = None
# 			created = None
# 			updated = None

# 			if('summary' in item):			
# 				# print('summary=>'+str(item['summary']))
# 				summary = item['summary']

# 			if('date' in item['start'] ):
# 				# print('start_date=>'+str(item['start']['date']))
# 				# print('end_date=>'+str(item['end']['date']))
# 				start_date = item['start']['date']
# 				end_date = item['end']['date']

# 			elif('dateTime' in item['start']):
				
# 				# print('remove utc ->'+str(item['start']['dateTime']) )
# 				start_date = utils.date_utc_to_current(str(item['start']['dateTime']))
# 				end_date = utils.date_utc_to_current(str(item['end']['dateTime']))
								
				
# 			created = str(item['created'])[:-1]
# 			updated = str(item['updated'])[:-1]

# 			db_manager.query(
# 				"INSERT INTO events " 
# 				"(calendar_id,event_id,summary,start_date,end_date,created,updated) "
# 				"VALUES "
# 				"(%s, %s, %s, %s, %s, %s, %s) ",
# 				(			
# 					calendar_id,event_id,summary,start_date,end_date,created,updated
# 				)
# 			)
# 		#해당 syncToken을 업데이트해준다.
# 		print('sync==>'+syncToken)
# 		db_manager.query(
# 			"INSERT INTO sync " 
# 			"(calendar_id,sync_token,ctime) "
# 			"VALUES "
# 			"(%s, %s, now()) ",
# 			(			
# 				calendar_id,syncToken
# 			)
# 		)		

# 	return 'list'	

#for event push 
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

	
