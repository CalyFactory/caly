#-*- coding: utf-8 -*-
# import sys 
# sys.path.append("../")

# import os
# from pathlib import Path
# print(Path(os.getcwd()).parent)

from celery import Celery
from celery.signals import worker_init
from celery.signals import worker_shutdown
from celery.bin.celery import result

import datetime
import requests
import json
import time
import random
import threading

from common import syncLogic
from common.util.statics import *

import logging


with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)


app = Celery('tasks', broker='amqp://'+conf['rabbitmq']['user']+':'+conf['rabbitmq']['password']+'@'+conf['rabbitmq']['hostname']+'//')


@worker_init.connect
def init_worker(**kwargs):
	print('init')

@worker_shutdown.connect
def shutdown_worker(**kwargs):
	print('shut')

#codereview
#nametask를 쓰느 이유.
@app.task(name='task')
def worker(data):
	gameThread = threading.Thread(target=run, args=(data,))
	gameThread.start()

def run(data):
	print("celery data : " + str(data))

	login_platform = data['login_platform']
	apikey = data['apikey']
	user = data['user']	
	if login_platform == 'naver' or login_platform == 'ical':	
		user_hashkey = data['user_hashkey']
		syncInfo = syncLogic.caldav(user,apikey,login_platform,SYNC_TIME_STATE_BACKWARD)
	elif login_platform == 'google':		
		syncInfo = syncLogic.google(user,apikey,SYNC_TIME_STATE_BACKWARD)

	print("syncInfo : " + str(syncInfo))

	return
