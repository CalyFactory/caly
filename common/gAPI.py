import json
from oauth2client import client
from model import userAccountModel
import logging
import requests
from common.util import utils

with open('./key/client_secret.json') as conf_json:
    conf = json.load(conf_json)

def getOauthCredentials(authCode):
    flow = client.flow_from_clientsecrets(					
    	'./key/client_secret.json',
    	scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.readonly',
    	redirect_uri='https://ssoma.xyz:55566/googleAuthCallBack'
    	
    )	
    flow.params['prompt'] = 'consent'   			
    # flow.params['include_granted_scopes'] = True
    # flow.params['access_type'] = 'offline'
    # flow.params['approval_prompt'] = 'force'

    credentials = json.loads(flow.step2_exchange(authCode).to_json())    
    return credentials

def getRefreshAccessToken(refresh_token):
    URL = 'https://www.googleapis.com/oauth2/v3/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    body = {
        'client_id' :conf['web']['client_id'],
        'client_secret': conf['web']['client_secret'],
        'grant_type' : 'refresh_token',
        'refresh_token': refresh_token
        
    }
    print(str(body))
    response = requests.post(URL,data = body,headers = headers)
   
    return response.text

def checkValidAccessToken(access_token):
    userAccount = userAccountModel.getUserAccountWithAccessToken(access_token)      
    logging.debug(userAccount)
    expire_time = userAccount[0]['google_expire_time']
    refresh_token = userAccount[0]['refresh_token']

    #유효할 경우    
    if utils.subDateWithCurrent(expire_time) < 0:
        logging.info('valid date')
        return 'valid date'
    #유효하지 않을 경우.
    #accesToken을 업데이트 시켜야한다.
    else:
        logging.info('update accessToken')      
        refresh_info = getRefreshAccessToken(refresh_token)
        logging.info('refresh info ==>' + refresh_info)
        return refresh_info




