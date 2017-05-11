import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import schedule
import time
from manager import db_manager

from common.util import utils

import json 

def job():
    users = utils.fetch_all_json(             
                db_manager.query(
                    '''
                    SELECT USERACCOUNT.user_hashkey FROM USERACCOUNT
                    INNER JOIN
                    (SELECT user_id,users.account_hashkey,users.user_hashkey FROM USER_LIFE_STATE 
                    INNER JOIN 
                    (SELECT apikey,USERACCOUNT.user_id,USERACCOUNT.account_hashkey,USERACCOUNT.user_hashkey FROM USERACCOUNT
                    INNER JOIN USERDEVICE ON USERACCOUNT.account_hashkey = USERDEVICE.account_hashkey
                    WHERE USERACCOUNT.is_active is not null ) as users
                    ON users.apikey = USER_LIFE_STATE.apikey
                    WHERE DATE(USER_LIFE_STATE.ctime) < (NOW() - INTERVAL 7 DAY)
                    GROUP BY users.account_hashkey) as noneActiveUsers
                    ON noneActiveUsers.user_hashkey = USERACCOUNT.user_hashkey
                    GROUP BY USERACCOUNT.user_hashkey

                    '''
                    ,
                    (                                   
                    )
                )

            )    

    additionQuery = ''
    for user in users:
        additionQuery += 'user_hashkey = "' + user['user_hashkey'] + '" or ' 

    additionQuery =  additionQuery[:len(additionQuery)-3]
    #                
    db_manager.query(
        '''
        UPDATE USERACCOUNT 
        SET is_active = 2
        '''
        +'WHERE '+ additionQuery
        
        ,
        (                                   
        )
    )

    



    return 'hi'

schedule.every().day.at("02:00").do(job)

job()

while True:
    schedule.run_pending()
    time.sleep(1)
