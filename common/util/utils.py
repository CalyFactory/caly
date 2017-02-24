from datetime import datetime
import hashlib
import time
import json
from time import gmtime, strftime
from datetime import datetime


loginState = lambda state,data : {'state':state,'data':data}

syncState = lambda state,data : {'state':state,'data':data}

def resSuccess(payload):
	return json.dumps(
						{'payload':payload}
					),200,{'Conent_Type':'application/json'}

def resErr(err):
	return json.dumps(
						{'payload':err}
					),400,{'Conent_Type':'application/json'}

def resCustom(code,payload):
	return json.dumps(
						{'payload':payload}
					),code,{'Conent_Type':'application/json'}			



def multiReturn(code,data,header):
	if header == 'json':
		header = 'application/json'	

	return data,code,{'Content-Type':'application/json'}


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

	