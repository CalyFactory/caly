# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import json 


with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

from pymongo import MongoClient
client = MongoClient('mongodb://'+conf["mongo"]["user"]+':' + conf["mysql"]["password"] + '@127.0.0.1')
base_db = client.calydb

#fcm
fcm = base_db.fcm



