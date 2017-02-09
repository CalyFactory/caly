# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import json 


with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)


# pool로 커낵션을 잡는다. 오토커밋 옵션을 false로해줘야한다.
engine = create_engine(
    'mysql+pymysql://'+conf["mysql"]["user"]+':'+conf["mysql"]["password"]+'@'+conf["mysql"]["host"]+'/'+conf["mysql"]["database"]+"?charset=utf8",
    pool_size = 20, 
    pool_recycle = 500, 
    max_overflow = 10,
    echo = True,
    echo_pool = True,
    execution_options = {"autocommit": True}
)
 
session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=False,
                                         bind=engine))

def query(queryString, params = None):
    i=0
    while '%s' in queryString:
        queryString = queryString.replace('%s', ':p'+str(i), 1)
        i+=1

    if params != None:
        params = list(params)
        args = {}
        for idx, arg in enumerate(params):
            key = 'p'+str(idx)
            args[key] = arg

        result = session.execute(queryString, args)
    else:
        result = session.execute(queryString)

    return result


