import os
os.environ["CALY_DB_CONF"] = "./key/conf.json"

from celery import Celery
from celery.task import periodic_task
from celery.schedules import crontab
from datetime import timedelta
from manager import db_manager
import json 
import time 
import caldavclient
import time
import uuid
from common.util import utils
from datetime import datetime
from pytz import timezone
from caldavclient import CaldavClient

from caldavclient.exception import AuthException
from common import cryptoo
import logging
from bot import slackAlarmBot
from common import FCM
from model import mFcmModel
from model import syncEndModel
from common.util.statics import *
from common import caldavPeriodicSync
import logging
import logging.handlers

# 
sqla_logger = logging.getLogger('sqlalchemy.engine.base.Engine')
for hdlr in sqla_logger.handlers:
    sqla_logger.removeHandler(hdlr)



with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)


app = Celery('tasks', broker='amqp://'+conf['rabbitmq']['user']+':'+conf['rabbitmq']['password']+'@'+conf['rabbitmq']['hostname']+'//', queue='periodicSyncQueue')
app.conf.task_default_queue = 'periodicSyncQueue'



@periodic_task(run_every=timedelta(seconds=300))
def accountDistributor():
    logging.info("hello")
    accountList = utils.fetch_all_json(
        db_manager.query(
            """
            SELECT * 
            FROM USERACCOUNT
            WHERE is_active != 3
            """
        )
    )

    for account in accountList:
        if account['login_platform'] == "google":
            continue    
        syncWorker.delay(account)
        

@app.task()
def syncWorker(account):
    
    # mylogger = logging.getLogger()
    # mylogger.setLevel(logging.DEBUG)
    # rotatingHandler = logging.handlers.TimedRotatingFileHandler(filename='log/'+'log_caldav_worker.log', when='midnight', interval=1, encoding='utf-8')
    # fomatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    # rotatingHandler.setFormatter(fomatter)
    # mylogger.addHandler(rotatingHandler)
    logging.info("hello")
    caldavPeriodicSync.sync(account)


            

