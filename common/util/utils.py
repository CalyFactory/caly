from datetime import datetime
import hashlib
import time
import json
from time import gmtime, strftime
from datetime import datetime


resSuccess = lambda payload : json.dumps({
											'code':200,
											'payload':payload
										})

resErr = lambda err : json.dumps({
									'code':400,
									'payload':err
								})

resCustom = lambda code,payload : json.dumps({'code':code,'payload':payload})

loginState = lambda state,data : {'state':state,'data':data}

syncState = lambda state,data : {'state':state,'data':data}

def subDateWithCurrent(date):
	cur_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())	
	#타임을 맞춰줘야함.
	time_stamp_cur = time.mktime(datetime.strptime(cur_date, '%Y-%m-%d %H:%M:%S').timetuple()) + 9*3600
	time_stamp_date = time.mktime(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timetuple())
	return time_stamp_cur - time_stamp_date
	


def makeHashKey(solt):
	soltt = str(solt)+str(time.time()*1000)
	print(soltt)
	soltt = soltt.encode('utf-8')
	return hashlib.sha224(soltt).hexdigest()

def makeHashKeyNoneTime(solf):

	soltt = str(solt+'secrettskkey')
	soltt = soltt.encode('utf-8')
	return hashlib.sha224(soltt).hexdigest()

def fetch_all_json(result):
	lis = []

	for row in result.fetchall():
		i = 0
		dic = {}

		for data in row:
			if type(data) == datetime:
				dic[result.keys()[i]]= str(data)
			else:
				dic[result.keys()[i]]= data
			if i == len(row)-1:
				lis.append(dic)

			i=i+1
	return lis

def date_utc_to_current(date):
	if(date.index('+') != -1):
		return date[:date.index('+')]	
	elif(date.index('-') != -1):
		return date[:date.index('-')]	

	