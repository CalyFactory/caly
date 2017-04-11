from celery import Celery
from celery.task import periodic_task
from celery.schedules import crontab
# from celery.task.schedules import crontab
# from celery.decorators import periodic_task


import logging
import schedule
import time
from datetime import date
from datetime import datetime, timedelta
import requests
from common.util import utils
from manager import db_manager
from common import gAPI
from model import calendarModel
from model import googleWatchInfoModel
from common.util.statics import *
import logging
import json 


with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

sqla_logger = logging.getLogger('sqlalchemy.engine.base.Engine')
for hdlr in sqla_logger.handlers:
    sqla_logger.removeHandler(hdlr)



with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)


app = Celery('tasks', broker='amqp://'+conf['rabbitmq']['user']+':'+conf['rabbitmq']['password']+'@'+conf['rabbitmq']['hostname']+'//', queue='periodicSyncQueue')
app.conf.task_default_queue = 'googleRetachQueue'





@periodic_task(run_every=crontab(hour=2, minute=30))
def init():
        retachWorker.delay()
        

@app.task()
def retachWorker():

    #현재 바꿔야할 캘린더들을 가져온다.
    calendars = calendarModel.getRetachGoogleWatchList()
    print('changed calendars = >'+str(calendars))
    #캘린더들중에
    for calendar in calendars:
        #채널에 해당하는 캘린더계정을 가져온다.
        account = calendarModel.getAccountHashkey(calendar['google_channel_id'])   
        access_token = account[0]['access_token']
        print(account)
        
        #현재 날자로부터 한달시간 설정.
        expp = datetime.now()+ timedelta(hours=MONTH_TO_HOUR)
        logging.info('exp =>'+str(expp))
        logging.info('exp =>'+str(expp.timestamp()))
        exp_unix_time = int(expp.timestamp()*1000) 
        logging.info('google expiration -> '+str(exp_unix_time))        


        print(calendar['google_channel_id'])
        print(calendar['google_resource_id'])
        print(access_token)
        #해당 모든계정을 stop시키고
        result = gAPI.stopWatch(calendar['google_channel_id'],calendar['google_resource_id'],access_token)
        print('reuslt => ' + result)
        if result == "":
            logging.info('stop watch Succes')
            googleWatchInfoModel.setGoogleWatchInfo(calendar['google_channel_id'],GOOGLE_WATCH_DETACH)

            res = gAPI.attachWatch(calendar['calendar_id'],calendar['google_channel_id'],'None',str(exp_unix_time)+'000',access_token)
            logging.info('watch res =>'+str(res))

            try:
                logging.info('giood') 
                logging.info(res['id']) 
                logging.info(expp) 
                logging.info(res['resourceId']) 

                calendarModel.updateGoogleExpiration(res['id'],expp,res['resourceId'])                  
            except Exception as e:
                logging.error(str(e)) 
                
            googleWatchInfoModel.setGoogleWatchInfo(calendar['google_channel_id'],GOOGLE_WATCH_CALL)            

        else:
            logging.info('faillllll')                       

        logging.info('result => '+result)                   
    
    return 0