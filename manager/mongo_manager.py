# #-*- coding: utf-8 -*-
from pymongo import MongoClient

import json 


with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

client = MongoClient('mongodb://'+conf["mongo"]["user"]+':' + conf["mysql"]["password"] + '@127.0.0.1')
base_db = client.calydb

#fcm
fcm = base_db.fcm



