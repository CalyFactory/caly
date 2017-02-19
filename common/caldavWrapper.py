from manager import db_manager
from caldavclient import CaldavClient
from common.util import utils

# class SingletonMetaClass(type):
#     def __init__(cls,name,bases,dict):
#         super(SingletonMetaClass,cls)\
#           .__init__(name,bases,dict)
#         original_new = cls.__new__
#         def my_new(cls,*args,**kwds):
#             if cls.instance == None:
#                 cls.instance = \
#                   original_new(cls,*args,**kwds)                
#             return cls.instance
#         cls.instance = None
#         cls.__new__ = staticmethod(my_new)



# @singleton
# class MyClass(BaseClass):
#     pass


# class caldavWrapper(object):
#     __metaclass__ = SingletonMetaClass
#     def __init__(self,val):
#         self.val = val
#     def __str__(self):
#         return 'self' + self.val
def getCalDavClient(login_platform,u_id,u_pw):
	if login_platform == 'naver':
		#codeReview 
		hostname = 'https://caldav.calendar.naver.com/principals/'
		# hostname = 'https://caldav.calendar.naver.com/principals/users/' + str(u_id)
	elif login_platform == 'ical':
		hostname = 'https://caldav.icloud.com/'

	#클라에서 loginState확인을 거쳐온 id/pw임으로 무조건 인증된 정보이다.
	calDavclient = CaldavClient(
	    hostname,
	    (u_id,u_pw)
	)
	
	return calDavclient;
		


# def updateCal(account_hashkey):
# 	client = CaldavClient(
# 	    'https://caldav.calendar.naver.com/principals/users/kkk1140' ,
# 	    'd',
# 	    'd'
# 	)

# 	principal = client.getPrincipal()
# 	homeset = principal.getHomeSet()
# 	calendars = homeset.getCalendars()


# 	arrQueryString = []
# 	arrQueryString.append('INSERT INTO CALENDAR (calendar_hashkey,account_hashkey,calendar_id,calendar_name,caldav_calendar_url,caldav_ctag) values ')
# 	for calendar in calendars:
# 		calendar_hashkey = utils.makeHashKey(calendar.calendarId)
# 		arrQueryString.append('("'+ calendar_hashkey +'","'+ account_hashkey + '","' + calendar.calendarId + '","'+ calendar.calendarName+'","'+calendar.calendarUrl+'","'+calendar.cTag+ '")')
# 		arrQueryString.append(',')

# 	arrQueryString.pop()
# 	lastQuery = "".join(arrQueryString)

# 	print('string=>'+str(lastQuery))
# 	db_manager.query(
# 						lastQuery
							
# 					)					
