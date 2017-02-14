from common.util import utils
from manager import db_manager

def setGoogleUserWithHashkey(user_hashkey):
	return 	db_manager.query(
				"INSERT INTO USER " 
				"(user_hashkey)"
				"VALUES"
				"(%s)",
				(			
					user_hashkey,
				)
			)