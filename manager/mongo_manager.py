# #-*- coding: utf-8 -*-
from pymongo import MongoClient

import json 


with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

client = MongoClient('mongodb://'+conf["mongo"]["user"]+':' + conf["mysql"]["password"] + '@127.0.0.1')
base_db = client.calydb

#fcm log
fcm = base_db.fcm
#event관련 log
event_log = base_db.event_log

reco_log = base_db.reco_log


account_list_log = base_db.account_list_log


