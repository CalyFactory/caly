

from slackclient import SlackClient
import schedule
import time
from datetime import date
from datetime import datetime, timedelta
import requests
from common.util import utils
from manager import db_manager


import json 
with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

token = conf["slack"]["token_daily"]
slackClient = SlackClient(token)


def getdate(dateString):
    dateObject = datetime.strptime(dateString, "Date(%Y,%m,%d,%H,%M,%S)")
    return dateObject.strftime("%H:%M")
def job():
    regit = utils.fetch_all_json(				
				db_manager.query(
					"select count(*) as users from USER where created > date_sub(now(), interval 1 day)"
					,
					(									
					)
				)

			)
    account = utils.fetch_all_json(             
                db_manager.query(
                    "select count(*) as users from USERACCOUNT where create_datetime > date_sub(now(), interval 1 day); "
                    ,
                    (                                   
                    )
                )

            )    
    text = (":coffee: 어제의 가입자수 :  " + str(regit[0]['users']) +
            "\n        어제의 등록 계정수 : " + str(account[0]['users'])             
            
    )
    slackClient.api_call(
        "chat.postMessage", 
        channel="#admin_daily_alert", 
        text=text,
        username='dailyBot', 
        icon_emoji=':octopus:'
    )
    return 0

schedule.every().day.at("09:00").do(job)

job()

while True:
    schedule.run_pending()
    time.sleep(1)
