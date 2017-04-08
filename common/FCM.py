import logging
from pyfcm import FCMNotification
import json 


with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

def send(push_tokens,title,body,data = {}):
	push_service = FCMNotification(api_key=conf["fcm"]["key"])
	message_title = title
	message_body = body

	if isinstance(push_tokens,list):
		logging.info('[push Multi]')
		result = push_service.notify_multiple_devices(registration_ids=push_tokens, message_title=message_title, message_body=message_body,data_message=data)
		return result
	else:
		logging.info('[push Single]')
		result = push_service.notify_single_device(registration_id=push_tokens, message_title=message_title, message_body=message_body,data_message=data)
		return result

def sendOnlyData(push_tokens,data = {}):
	push_service = FCMNotification(api_key=conf["fcm"]["key"])

	if isinstance(push_tokens,list):
		logging.info('[push Multi]')
		result = push_service.notify_multiple_devices(registration_ids=push_tokens, data_message=data)						
		return result		
	else:
		logging.info('[push Single]')
		result = push_service.notify_single_device(registration_id=push_tokens, data_message=data)
		return result		
