import requests
import json
from flask import Flask,session
from manager.redis import redis
def reqPOST(URL,body = {}):
	print('aT=>'+str(redis.get('user_access_token')))
	#여기서 Authorization Bearer 뒤에 값은 유저 액세스 토큰이다.
	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + str(redis.get('user_access_token'))
	}
	response = requests.post(URL,data = json.dumps(body),headers = headers)
	return response.text

def reqGET(URL,params = {}):
	
	print('aT=>'+str(redis.get('user_access_token')))
	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + str(redis.get('user_access_token'))
		
	}	
	response = requests.get(URL,params = params,headers = headers)
	return response.text