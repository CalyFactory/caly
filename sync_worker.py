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



app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')


@worker_init.connect
def init_worker(**kwargs):
	print('init')

@worker_shutdown.connect
def shutdown_worker(**kwargs):
	print('shut')

@app.task(name='task')
def worker(data):
	gameThread = threading.Thread(target=run, args=(data,))
	gameThread.start()

def run(data):
	print("celery data : " + str(data))

	login_platform = data['login_platform']
	
	if login_platform == 'naver' or login_platform == 'ical':
		user = data['user']
		user_hashkey = data['user_hashkey']
		syncInfo = syncLogic.caldav(user,apikey,login_platform,SYNC_TIME_STATE_BACKWARD)
	elif login_platform == 'google':
		user = data['user']
		apikey = data['apikey']
		syncInfo = syncLogic.google(user,apikey,SYNC_TIME_STATE_BACKWARD)

	print("syncInfo : " + str(syncInfo))

	return
