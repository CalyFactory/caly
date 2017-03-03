from common.util import utils
from manager import db_manager

def setUserLifeState(apikey,state):
	return db_manager.query(
				"INSERT INTO USER_LIFE_STATE (apikey,state) " 
				"VALUES(%s,%s)"
				,
				(apikey,state)
			)
