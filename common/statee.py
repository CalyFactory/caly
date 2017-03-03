from model import userLifeModel
from common.util.statics import *

def userLife(apikey,state):
	try:										
		userLifeModel.setUserLifeState(apikey,LIFE_STATE_SIGNUP)
	except Exception as e:
		logging.error(str(e))