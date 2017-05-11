# #-*- coding: utf-8 -*-
import logging
import logging.handlers


## 인스턴스만들기.
mylogger = logging.getLogger()
mylogger.setLevel(logging.INFO)
rotatingHandler = logging.handlers.TimedRotatingFileHandler(filename='log/'+'log_caly.log', when='m', interval=1, encoding='utf-8')
fomatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
rotatingHandler.setFormatter(fomatter)
mylogger.addHandler(rotatingHandler)

# logging = mylogger

# class Singleton(object):
#   _instance = None
#   def __new__(class_, *args, **kwargs):
#     if not isinstance(class_._instance, class_):
#         class_._instance = object.__new__(class_, *args, **kwargs)
#     return class_._instance

# class logger(Singleton):
  
# 	# 인스턴스만들기.
# 	mylogger = logging.getLogger('MyLogger')
# 	mylogger.setLevel(logging.INFO)

# 	rotatingHandler = logging.handlers.TimedRotatingFileHandler(filename='log/'+ str(datetime.now())+'_log_caly.log', when='s', interval=1, encoding='utf-8')
# 	fomatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
# 	rotatingHandler.setFormatter(fomatter)
# 	mylogger.addHandler(rotatingHandler)

# 	def getLogger(self):
# 		return self.mylogger
