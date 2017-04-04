from slackclient import SlackClient
from datetime import datetime

import json 
with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

token = conf["slack"]["token_sync"]
sync_channel = conf["slack"]["sync_channel"]
slackClient = SlackClient(token)

def alertSyncEnd():
	text = (":exclamation: 유저의 동기화가 끝났습니다. 이벤트 매칭해주세요 \n" +
			":clock3: 동기화 시간:"+str(datetime.now())	        
			)

	slackClient.api_call(
		"chat.postMessage",
		channel=sync_channel,
		text=text,
		username='syncBot',
		icon_emoji=':crab:'
		)

def alertEventUpdateEnd(eventType):
	text = (":part_alternation_mark: 유저의 일정이 " + eventType + " 됬습니다. 이벤트 매칭해주세요 \n" +
			":clock3: 엄데이트 시간:"+str(datetime.now())	        
			)

	slackClient.api_call(
		"chat.postMessage",
		channel=sync_channel,
		text=text,
		username='syncBot',
		icon_emoji=':chipmunk:'
		)	