import json
from oauth2client import client

def getOauthCredentials(authCode):
	flow = client.flow_from_clientsecrets(					
		'./key/client_secret.json',
		scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.readonly',
		redirect_uri='https://ssoma.xyz:55566/googleAuthCallBack'
	)				
	flow.params['access_type'] = 'offline'
	flow.params['approval_prompt'] = 'force'
	credentials = json.loads(flow.step2_exchange(authCode).to_json())

	return credentials