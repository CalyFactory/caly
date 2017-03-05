#-*- coding: utf-8 -*-

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
import logging
 

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')


@worker_init.connect
def init_worker(**kwargs):
	print('init')

@worker_shutdown.connect
def shutdown_worker(**kwargs):
	print('shut')

@app.task
def worker(data):
    gameThread = threading.Thread(target=run, args=(data,))
    gameThread.start()

def run(data):
    
    print("celery data : " + str(data))
