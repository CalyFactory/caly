import json
from oauth2client import client
import requests
with open('./key/client_secret.json') as conf_json:
    conf = json.load(conf_json)

def getOauthCredentials(authCode):
    flow = client.flow_from_clientsecrets(					
    	'./key/client_secret.json',
    	scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.readonly',
    	redirect_uri='https://ssoma.xyz:55566/googleAuthCallBack'
    	
    )	
    flow.params['prompt'] = 'consent'   			
	#     # flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
 #     #                       client_secret=CLIENT_SECRET,
 #     #                       scope='https://spreadsheets.google.com/feeds https://docs.google.com/feeds',
 #     #                       redirect_uri='http://example.com/auth_return',
 #     #                       prompt='consent')
    # flow.params['include_granted_scopes'] = True
    # flow.params['access_type'] = 'offline'
    # flow.params['approval_prompt'] = 'force'

    credentials = json.loads(flow.step2_exchange(authCode).to_json())
    # from oauth2client.client import OAuth2WebServerFlow
    # from oauth2client.tools import run_flow
    # from oauth2client.file import Storage

    # CLIENT_ID = '<client_id>'
    # CLIENT_SECRET = '<client_secret>'
    # flow = OAuth2WebServerFlow(client_id='881274260597-26b4e9bqah6nbp1katm5qlud3gfitlat.apps.googleusercontent.com',
    #                        client_secret='_c7xYf52EQ3GFKTVvftThQlF',
    #                        scope='https://spreadsheets.google.com/feeds https://docs.google.com/feeds',
    #                        redirect_uri='http://example.com/auth_return',
    #                        prompt='consent')
    # storage = Storage('creds.data')
    # credentials = run_flow(flow, storage)
    return credentials

def getRefreshAccessToken(refresh_token):
    URL = 'https://www.googleapis.com/oauth2/v3/token'
    headers = {
        'content-Type': 'application/x-www-form-urlencoded'
    }
    body = {
        'client_id' :conf['web']['client_id'],
        'client_secret': conf['web']['client_secret']+'&',
        'refresh_token':refresh_token,
        'grant_type':'refresh_token'
    }
    print('body'+str(body))
    response = requests.post(URL,data = json.dumps(body),headers = headers)
    print(str(response))
    return json.loads(response)
