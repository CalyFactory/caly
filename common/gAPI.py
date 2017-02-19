import json
from oauth2client import client

def getOauthCredentials(authCode):
    flow = client.flow_from_clientsecrets(					
    	'./key/client_secret.json',
    	scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.readonly',
    	redirect_uri='https://ssoma.xyz:55566/googleAuthCallBack'
    	
    )				
	#     # flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
 #     #                       client_secret=CLIENT_SECRET,
 #     #                       scope='https://spreadsheets.google.com/feeds https://docs.google.com/feeds',
 #     #                       redirect_uri='http://example.com/auth_return',
 #     #                       prompt='consent')
    flow.params['include_granted_scopes'] = True
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'

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