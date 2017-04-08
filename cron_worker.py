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

sqla_logger = logging.getLogger('sqlalchemy.engine.base.Engine')
for hdlr in sqla_logger.handlers:
    sqla_logger.removeHandler(hdlr)



with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)


app = Celery('tasks', broker='amqp://'+conf['rabbitmq']['user']+':'+conf['rabbitmq']['password']+'@'+conf['rabbitmq']['hostname']+'//', queue='periodicSyncQueue')
app.conf.task_default_queue = 'periodicSyncQueue'


def getHostname(login_platform):
    if login_platform == "naver":
        return "https://caldav.calendar.naver.com:443/principals/"
    elif login_platform == "ical":
        return "https://caldav.icloud.com"
    return "https://caldav.icloud.com"

def findEvent(eventList, eventId):
    for event in eventList:
        if event.eventUrl == eventId:
            return event

def findEventList(eventList, eventIdList):
    eventObjectList = []
    for eventId in eventIdList:
        eventObjectList.append(findEvent(eventList, eventId))
    return eventObjectList



@periodic_task(run_every=timedelta(seconds=300))
def accountDistributor():
    print("hello")
    
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
    print("start sync check")
    calendars = utils.fetch_all_json(
        db_manager.query(
            """
            SELECT *
            FROM CALENDAR
            WHERE 
            `account_hashkey` = %s
            """
            ,
            (
                account['account_hashkey'],
            )
        )
    )
    calendarList = []
    for calendar in calendars:
        calendarList.append(
            CaldavClient.Calendar(
                calendarUrl = calendar['caldav_calendar_url'],
                calendarName = calendar['calendar_name'],
                cTag = calendar['caldav_ctag'],
                etc = calendar['calendar_hashkey']
            )
        )
    
    client = (
        CaldavClient(
            hostname = getHostname(account['login_platform']),
            auth = (
                account['user_id'],
                cryptoo.decryptt(account['access_token'])

            )
        ).setCalendars(calendarList)       #db에서 로드해서 list calendar object 로 삽입
        #.setPrincipal(account['home_set_cal_url'])   #db 에서 로드 
        #.setHomeSet(account['home_set_cal_url'])  #db 에서 로드 
    )

    for calendar in calendarList:
        
        try:
            isChanged = calendar.isChanged()
        except AuthException as e:
            print("error") # 요기서 처리하시면 됩니당 ^_^
            #1. account state 2로만든다.
            # 잘로그인됬으면 1
            # 비활성유저는 2 
            # 로그인 실패상황이면 3
            #2. 유저한테 push Notification을 보낸다. => 비밀번호 업데이트하세여.
          

            db_manager.query(
                """
                UPDATE USERACCOUNT
                SET is_active = 3
                WHERE 
                `account_hashkey` = %s
                """
                ,
                (
                    account['account_hashkey'],
                )
            )

            #모든계정으로 push
            #push 토큰구하기ㅕㄴㄷㄱ
            devices = utils.fetch_all_json(
                db_manager.query(
                    """
                    SELECT *
                    FROM USERDEVICE
                    WHERE 
                    `account_hashkey` = %s
                    """
                    ,
                    (
                        account['account_hashkey'],
                    )
                )
            )

            arr_push_token = []
            for device in devices:
                arr_push_token.append(device['push_token'])
                # arr_push_token.append(device['push_token'])

            data_message = {
                "type" : "account_update",
                "action" : "default"
            }
            
            result = FCM.sendOnlyData(arr_push_token,data_message)                
            result[0]['push_token'] = arr_push_token
            result[0]['push_data'] = data_message            
            mFcmModel.insertFcm(result)
            break;

            print(e)
            continue
        except Exception as e:
            print("error")
            print(e)
            continue

        if isChanged:
            print("something changed")
            print(calendar.etc)
            oldEventList = caldavclient.util.eventRowToList( #db에서 이전 event리스트들을 불러옴 
                utils.fetch_all_json(
                    db_manager.query(
                        """
                        SELECT *
                        FROM EVENT
                        WHERE 
                        `calendar_hashkey` = %s
                        """
                        ,
                        (
                            calendar.etc #calendar hashkey
                            ,
                        )
                    )
                )
            )
            newEventList = calendar.updateAllEvent()


            print(oldEventList)
            for event in newEventList:
                print(event.eventUrl)

            eventDiff = caldavclient.util.diffEvent(oldEventList, newEventList)


            #각각 추가삭제변경된 일정은 eventDiff.added(), removed(), changed()에서 리스트로 가져올 수 있음.
            print("추가 :" + str(len(eventDiff.added())))
            print("삭제 :" + str(len(eventDiff.removed())))
            print("변경 :" + str(len(eventDiff.changed())))

            print(eventDiff.added())
            print(eventDiff.removed())
            print(eventDiff.changed())
            
            
            if len(eventDiff.added()) != 0:
                addEvent(calendar, newEventList, eventDiff.added())
            if len(eventDiff.removed()) !=0:
                removeEvent(calendar, newEventList, eventDiff.removed())
            if len(eventDiff.changed()) !=0:
                changeEvent(calendar, newEventList, eventDiff.changed())

            db_manager.query(
                """
                UPDATE CALENDAR 
                SET 
                `caldav_ctag` = %s,
                `reco_state` = 1
                WHERE 
                `calendar_hashkey` = %s
                """,
                (
                    calendar.cTag,
                    calendar.etc
                )
            )


            

def addEvent(calendar, newEventList, addedList):
    print("일정이 추가되었다.")

    for event in calendar.getCalendarData(findEventList(newEventList, list(addedList))):
        
        item = event.eventData['VEVENT']
        print(item)

        if 'SUMMARY' in item:
            summary = item['SUMMARY']
        
        if 'DTSTART' in item:			

            start_dt = item['DTSTART']
            # datetime일경우만
            if(isinstance(start_dt,datetime)):
                #한국시간으로바꿔준다
                start_dt = start_dt.astimezone(timezone('Asia/Seoul'))

        if 'DTEND' in item:
            end_dt = item['DTEND']
            if(isinstance(end_dt,datetime)):
                #한국시간으로바꿔준다
                end_dt = end_dt.astimezone(timezone('Asia/Seoul'))					  
        
        #타임존 라이브러리정하기
        if 'CREATED' in item:
            created_dt = item['CREATED']
            if(isinstance(created_dt,datetime)):
                created_dt =created_dt.astimezone(timezone('Asia/Seoul'))					  			
        #문자열을 날짜시간으로 변경해줌. 
        # created_dt = datetime.strptime(created_dt, "%Y%m%dT%H%M%S") + timedelta(hours=9)		


        if 'LAST-MODIFIED' in item:
            updated_dt = item['LAST-MODIFIED']

        if(isinstance(updated_dt,datetime)):
                #한국시간으로바꿔준다
            updated_dt =updated_dt.astimezone(timezone('Asia/Seoul'))					  							
            
        else:		
            updated_dt = created_dt

        if 'LOCATION' in item:	
            if item['LOCATION'] == '':
                location = None
            else:
                location = item['LOCATION']
        db_manager.query(
            """
            INSERT INTO EVENT
            (
                `event_hashkey`,
                `calendar_hashkey`,
                `event_id`,
                `caldav_event_url`,
                `caldav_etag`,
                `summary`,
                `start_dt`,
                `end_dt`,
                `created_dt`,
                `updated_dt`,
                `location`
            )
            VALUES 
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """
            ,
            (
                str(uuid.uuid4()),
                calendar.etc, #calendar hashkey
                event.eventId,
                event.eventUrl,
                event.eTag,
                summary,
                start_dt,
                end_dt,
                created_dt,
                updated_dt,
                location

            )
        )
    slackAlarmBot.alertEventUpdateEnd("추가")        
    

def removeEvent(calendar, newEventList, removedList):
    print("일정이 삭제되었다.")
    for eventId in list(removedList):
                
        db_manager.query(
            """
            DELETE FROM EVENT
            WHERE 
            `caldav_event_url` = %s
            """
            ,
            (
                eventId,

            )
        )

def changeEvent(calendar, newEventList, changedList):
    print("일정이 변경되었다.") 

    for event in calendar.getCalendarData(findEventList(newEventList, list(changedList))):
        
        item = event.eventData['VEVENT']
        print(item)

        if 'SUMMARY' in item:
            summary = item['SUMMARY']
        
        if 'DTSTART' in item:			

            start_dt = item['DTSTART']
            # datetime일경우만
            if(isinstance(start_dt,datetime)):
                #한국시간으로바꿔준다
                start_dt = start_dt.astimezone(timezone('Asia/Seoul'))

        if 'DTEND' in item:
            end_dt = item['DTEND']
            if(isinstance(end_dt,datetime)):
                #한국시간으로바꿔준다
                end_dt = end_dt.astimezone(timezone('Asia/Seoul'))					  
        
        #타임존 라이브러리정하기
        if 'CREATED' in item:
            created_dt = item['CREATED']
            if(isinstance(created_dt,datetime)):
                created_dt =created_dt.astimezone(timezone('Asia/Seoul'))					  			
        #문자열을 날짜시간으로 변경해줌. 
        # created_dt = datetime.strptime(created_dt, "%Y%m%dT%H%M%S") + timedelta(hours=9)		


        if 'LAST-MODIFIED' in item:
            updated_dt = item['LAST-MODIFIED']

        if(isinstance(updated_dt,datetime)):
                #한국시간으로바꿔준다
            updated_dt =updated_dt.astimezone(timezone('Asia/Seoul'))					  							
            
        else:		
            updated_dt = created_dt

        if 'LOCATION' in item:	
            if item['LOCATION'] == '':
                location = None
            else:
                location = item['LOCATION']
        db_manager.query(
            """
            UPDATE EVENT
            SET
            `caldav_etag` = %s,
            `summary` = %s,
            `start_dt` = %s,
            `end_dt` = %s,
            `created_dt` = %s,
            `updated_dt` = %s,
            `location` = %s,
            `reco_state` = 1
            WHERE 
            `event_id` = %s
            """
            ,
            (
                event.eTag,
                summary,
                start_dt,
                end_dt,
                created_dt,
                updated_dt,
                location,
                event.eventId

            )
        )
    slackAlarmBot.alertEventUpdateEnd("변경")