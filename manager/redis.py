
#-*- coding: utf-8 -*-
import redis
redis = redis.StrictRedis(host='127.0.0.1',port=6379,db=0,charset="utf-8", decode_responses=True)
