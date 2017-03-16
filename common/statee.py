from model import userLifeModel
from common.util.statics import *
import logging

def userLife(apikey,state):
	try:										
		userLifeModel.setUserLifeState(apikey,state)
	except Exception as e:
		logging.error(str(e))