import requests
import json
from flask import Flask,session
from manager.redis import redis
from model import userAccountModel
from common.util import utils
from common import gAPI
import logging
def reqPOST(URL,accessToken,body = {}):
	
	#여기서 Authorization Bearer 뒤에 값은 유저 액세스 토큰이다.
	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + accessToken
	}
	response = requests.post(URL,data = json.dumps(body),headers = headers)
	return response.text

def reqGET(URL,accessToken,params = {}):
		
	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + accessToken
		
	}	
	response = requests.get(URL,params = params,headers = headers)
	return response.text

