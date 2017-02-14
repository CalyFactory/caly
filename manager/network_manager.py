import requests
import json
from flask import Flask,session
from manager.redis import redis
def reqPOST(URL,accessToken,body = {}):
	print('aT=>'+str(redis.get('user_access_token')))
	#여기서 Authorization Bearer 뒤에 값은 유저 액세스 토큰이다.
	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + accessToken
	}
	response = requests.post(URL,data = json.dumps(body),headers = headers)
	return response.text

def reqGET(URL,accessToken,params = {}):
	
	print('aT=>'+str(redis.get('user_access_token')))
	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + accessToken
		
	}	
	response = requests.get(URL,params = params,headers = headers)
	return response.text