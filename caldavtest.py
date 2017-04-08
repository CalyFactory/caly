from caldavclient import CaldavClient
import json 
import time 
from caldavclient import util
import time


with open('key.json') as json_data:
    d = json.load(json_data)
    userId = d['naver']['id']
    userPw = d['naver']['pw']

"""

hostname 

apple : https://caldav.icloud.com/
naver : https://caldav.calendar.naver.com/principals/users/{유저아이디}

참고로 애플은 유저 아이디가 이메일이고 네이버는 그냥 아이디에요 
"""
hostname = "https://caldav.calendar.naver.com/principals/users/jspiner"

## 기본 client 생성
client = CaldavClient(
    hostname,
    (userId, userPw)
) 
print("init")
principal = client.getPrincipal() # 유저 인증정보가 들어있는 클래스. 사실상 아무짝에도 안쓰임
print("principal")
homeset = principal.getHomeSet() # 캘린더 목록을 호출할 수 있는 정보가 들어있는 클래스. homeset주소를 디비에 넣어야함 ㅇㅇ 
print("homeset")
calendars = homeset.getCalendars() # 캘린더 리스트를 이렇게 받아옴
print("calendar")

#캘린더 이름 출력하기 예제

#for calendar in calendars:
#    print(calendar.calendarName + " " + calendar.calendarId + " " + calendar.cTag)

#이벤트 정보 출력하기 예제 
eventList = calendars[0].getAllEvent() #요렇게 캘린더 하나 선택해서 getAllEvent 호출하시면 됩니다 ^_^
eventList = calendars[0].getCalendarData(eventList)

print(len(eventList))
for event in eventList:
    print (event.eventId + " " + event.eTag)
