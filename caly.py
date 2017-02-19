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

#route 안에 googleAuth파일로 들어가서 클래스인 GoogleAuth를 임포트하겠다.
from route.googleAuth import GoogleAuth
from route.schedule import Schedule

from route.routes import initRoute

from flask import render_template
from flask import redirect, url_for,session
from common import redisSession
from caldavclient import CaldavClient

app = flask.Flask(__name__, static_url_path='')
# import logging
# logging.info("I told you so")

initRoute(app)

import logging
import optparse

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}


def main():
  parser = optparse.OptionParser()
  parser.add_option('-l', '--logging-level', help='Logging level')
  parser.add_option('-f', '--logging-file', help='Logging file name')
  (options, args) = parser.parse_args()
  logging_level = LOGGING_LEVELS.get(options.logging_level, logging.NOTSET)
  logging.basicConfig(level=logging_level, filename=options.logging_file,
                      format='%(asctime)s %(levelname)s: %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')

# with open('./APP_CONFIGURE.json') as conf_json:
# 	app_conf = json.load(conf_json)			

# app_version = '1.0.0'
# if app_version == 'null':
# 	pass						
# elif app_version == app_conf['version']	:
# 	print('nice')
# 	# return utils.resCustom(200,{'msg':'your version so nice!'})
# else :
# 	print('basd')
	# return utils.resCustom(205,{'msg':'강제업데이트 필요'})

##############
#  테스트요청	 #
##############
# from common import caldavWrapper
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

	# from pyfcm import FCMNotification
	# push_service = FCMNotification(api_key="AAAAzTAKDHU:APA91bE60nkbS9rIEqZbAmhjFTu3jFeYL1wPTnDpVZKEtTf4p02hipmCEMpF8ZhflRo_8Ofb2EspYKqpSoWR1qxKw8mDA4d1HxGSCordjbUwpOGlt1PP5gtcGGTET74xxk5bS0gGv2ig")
	# registration_id = ["cFK43rjMHoQ:APA91bE3HyJ1BVCI2Xrq3YJCrFll1Cjea3n8wVavHKiYVm1ktzRnbOrwICaSlBOcRP7Vg4c7fAFhBV4JdZd3fF-FZ49G8EgYgiozpKVAuXKU-3eI5YLleqghdBI521gvS4W_soc-vd4v","ejmnO9bSKDs:APA91bHyHu_W-jnnYWQqzEmvmlNarRZqJYEsC_6UHPCjpHmV0-0YrLA0-PXvfpYLarXg62qhZ6b_GFpg8yfqTL_fm8EEvM5PViF6mVbjSrSN4su9NwrY9bngzQSUMynJIB4LAIsSWzbl"]
	# message_title = "Uber update"
	# message_body = "Hi john, your customized news for today is ready"
	# # result = push_service.notify_single_device(registration_ids=registration_id, message_title=message_title, message_body=message_body)
	# result = push_service.notify_multiple_devices(registration_ids=registration_id, message_title=message_title, message_body=message_body)
	
	from common import FCM

	pks = "dtolwBZTUXk:APA91bH0WSHNkw8sF7syIMKKcyjmzpeUEh4NzsAenuaNPX36lOwezlz0_X7yVp8b2CUmFKoo1lJkKFXiEPcex9LgOj2RqV07Rdgxy17PEAOfDIMVblJC4Pss-HHGpf7v8WLsPIEUVXx-"
	arr = ["cFK43rjMHoQ:APA91bE3HyJ1BVCI2Xrq3YJCrFll1Cjea3n8wVavHKiYVm1ktzRnbOrwICaSlBOcRP7Vg4c7fAFhBV4JdZd3fF-FZ49G8EgYgiozpKVAuXKU-3eI5YLleqghdBI521gvS4W_soc-vd4v","ejmnO9bSKDs:APA91bHyHu_W-jnnYWQqzEmvmlNarRZqJYEsC_6UHPCjpHmV0-0YrLA0-PXvfpYLarXg62qhZ6b_GFpg8yfqTL_fm8EEvM5PViF6mVbjSrSN4su9NwrY9bngzQSUMynJIB4LAIsSWzbl"]
	data_message = {
	    "type" : "sync",
	    "action" : "actions"
	}
	print(FCM.sendOnlyData(token,data_message))
	return FCM.sendOnlyData(token,data_message)
	# return FCM.send(pks,'title','body',data_message)


@app.route('/teCaldavEvent')
def teCaldavEvent():
	with open('./key/conf.json') as conf_json:
	    conf = json.load(conf_json)
	    userId = conf['naver']['id']
	    userPw = conf['naver']['pw']
	    print(userId)
	    print(userPw)
	clientcal = CaldavClient(
		    'https://caldav.calendar.naver.com/principals/users/'+userId,
		    (userId,userPw)	    
		)

	principal = clientcal.getPrincipal()
	homeset = principal.getHomeSet()
	calendars = homeset.getCalendars()

	for calendar in calendars:
	    print('calnedarsss=> '+calendar.calendarName + " " + calendar.calendarUrl + " " + calendar.cTag)

	    eventList = calendar.getEventByRange( "20151117T000000Z", "20170208T000000Z")
	    print('evetnsList = >'+ str(eventList))
	    eventDataList = calendar.getCalendarData(eventList)
		# print('eventDataList = >'+ str(eventDataList))
	    for _ in eventDataList:
			#리턴이 배열이라면 여러개가 올수도있나요?

		    event = _.eventData['VCALENDAR'][0]['VEVENT'][0]
		    print(_)
		    # print('event==>'+str(_.eventId))
		    # print('event==>'+str(_.eventUrl))

			#임시
		    calendar_hashkey = 'd18b6c447d2896fd591f38e9b2a4a134f0804a65f4e281d653d3db45'
		    
		    # #uid를 eventId로 쓰면되나
		    event_id = _.eventId
		    event_hashkey = utils.makeHashKey(event_id)
		    # eventurl은 무엇을 저장해야되나여
		    caldav_event_url = _.eventUrl
		    #etag는 어디서 얻을수 있죠?
		    caldav_etag = _.eTag
		    summary = event['SUMMARY']
		    print('sum'+summary)
		    start_dt = None
		    end_dt = None

		    for _ in event.keys():
		    	if 'DTSTART' in _:
		    		print('find start ! =>'+_)
		    		start_dt = event[_] 
		    	elif 'DTEND' in _:
		    		print('find end ! =>'+_)
		    		end_dt = event[_]

		    created_dt = event['CREATED'][:-1]
		    created_dt =datetime.strptime(created_dt, "%Y%m%dT%H%M%S") + timedelta(hours=9)	    


		    if 'LAST-MODIFIED' in event:
		        # print('has modifie')
		        updated_dt = event['LAST-MODIFIED'][:-1]
		        updated_dt = datetime.strptime(updated_dt, "%Y%m%dT%H%M%S") + timedelta(hours=9)
		    else:		
			    updated_dt = created_dt
		    if event['LOCATION'] == '':
		    	location = 'noLocation'
		    else:
		    	location = event['LOCATION']

		 #    if '' == event['LOCATION':
			#     location = 'noLocation'
			# else:
		 #        location = event['LOCATION']

		    #print(calendar_hashkey)
		    # print(event_hashkey)
		    # print(event_id)
		    # print(caldav_event_url)
		    # print(caldav_etag)
		    #print(summary)
		    #print(start_dt)
		    #print(end_dt)
		    #print(created_dt)
		    #print(updated_dt)
		    #print(location)
		    try:
		    	from model import eventModel

		    	eventModel.setCaldavEvents(event_hashkey,calendar_hashkey,event_id,summary,start_dt,end_dt,created_dt,updated_dt,location,caldav_event_url,caldav_etag)
		    except Exception as e:
		    	return str(e)


			 
			
		#최초 생성일경우 updated는 created랑 같다.	

		# #수정이 생길경우 LAST-MODIFIED가 존재한다.
		

		
	    # start_dt = event[] a.split(':')



	return 'hi'


if __name__ == '__main__':
	main() 
	logging.debug("디버깅용 로그~~")
	logging.info("도움이 되는 정보를 남겨요~")
	logging.warning("주의해야되는곳!")
	logging.error("에러!!!")
	logging.critical("심각한 에러!!")
			
	#session사용응ㄹ 위해선 secret_key가 존재해야한다.	
	# md5를 사용한다고합니다 uuid4
	# app.secret_key = str(uuid.uuid4())	
	# app.session_interface = redisSession.RedisSessionInterface()
	
	
		# app.permanent_session_lifetime = timedelta(seconds=3600)

	ssl_context = ('./key/last.crt', './key/ssoma.key')
	app.run(host='0.0.0.0', debug = True, port = 55566, ssl_context = ssl_context,threaded=True)

	
