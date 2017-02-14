from datetime import datetime
import hashlib
import time
import json

resSuccess = lambda payload : json.dumps({'code':200,'payload':payload})
resErr = lambda err : json.dumps({'code':400,'payload':err})
resCustom = lambda code,payload : json.dumps({'code':code,'payload':payload})

loginState = lambda state,data : {'state':state,'data':data}

def makeHashKey(solt):
	soltt = str(solt)+str(int(time.time()))
	soltt = soltt.encode('utf-8')
	return hashlib.sha224(soltt).hexdigest()
	# m = hashlib.md5()
	# m.update(soltt)
	# return m.digest().decode('')

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

	