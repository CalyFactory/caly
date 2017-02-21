import requests
import json
from flask import Flask,session
from manager.redis import redis
from model import userAccountModel
from common.util import utils
from common import gAPI
import logging
def reqPOST(URL,access_token,body = {}):
	
	#있으면 바꿔줘야되고
	#없으면 기존것을 사용해야함.
	new_access_token = gAPI.checkValidAccessToken(access_token)	
	logging.debug('newacces=>'+ str(new_access_token))
	
	if new_access_token:
		logging.debug('new!')
		access_token = new_access_token


	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + access_token
	}
	response = requests.post(URL,data = json.dumps(body),headers = headers)
	return response.text

def reqGET(URL,access_token,params = {}):
	
	new_access_token = gAPI.checkValidAccessToken(access_token)	
	logging.debug('newacces=>'+ str(new_access_token))
	if new_access_token:		
		access_token = new_access_token
		
	headers = {
		'content-Type': 'application/json',
		'Authorization' : 'Bearer ' + access_token
		
	}	
	response = requests.get(URL,params = params,headers = headers)
	return response.text

