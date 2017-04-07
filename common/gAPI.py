import json
from oauth2client import client
from model import userAccountModel
import logging
import requests
from common.util import utils
import datetime
from manager import network_manager

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
    logging.info('checkValidAccesToken')      

    userAccount = userAccountModel.getUserAccountWithAccessToken(access_token)      
    logging.debug(userAccount)
    expire_time = userAccount[0]['google_expire_time']
    refresh_token = userAccount[0]['refresh_token']
    logging.debug(expire_time)
    
    #유효할 경우    
    if utils.subDateWithCurrent(expire_time) < 0:
        logging.info('valid date')
        return 
    #유효하지 않을 경우.
    #accesToken을 업데이트 시켜야한다.
    else:

        logging.info('update accessToken')      
        refresh_info = json.loads(getRefreshAccessToken(refresh_token))
        logging.info('refresh info =>'+str(refresh_info) )
        new_access_token = refresh_info['access_token']
        expires_in = refresh_info['expires_in']

        current_date_time = datetime.datetime.now()
        google_expire_time = current_date_time + datetime.timedelta(seconds=expires_in)
        logging.debug('google expire tiem =>'+str(google_expire_time))
        try:
            userAccountModel.updateUserAccessToken(access_token,new_access_token,google_expire_time)
        except Exception as e:
            logging.debug(str(e))

        return new_access_token


def stopWatch(channel_id,resource_id,access_token):    

    URL = 'https://www.googleapis.com/calendar/v3/channels/stop'
    body = {
        "id" : channel_id,
        "resourceId": resource_id
    }
    result = network_manager.reqPOST(URL,access_token,body)   
    # print(network_manager.reqPOST(URL,body))
    return result     