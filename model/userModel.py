from common.util import utils
from manager import db_manager
#login_manager
#member.py
def setUser(user_hashkey,gender,birth):
	return 	db_manager.query(
				"INSERT INTO USER " 
				"(user_hashkey,user_gender,user_birth)"
				"VALUES"
				"(%s, %s, %s)",
				(			
					user_hashkey,
					gender,
					birth
				)
			)

def updateUserIsActive(user_hashkey,state):
	return 	db_manager.query(
				"UPDATE USER SET is_active = %s " 
				"WHERE user_hashkey  = %s "				
				,
				(			
					state,user_hashkey
				)
			)

def getUserIsActive(user_hashkey):
	return utils.fetch_all_json(
					db_manager.query(
						"SELECT is_active FROM USER " 
						"WHERE user_hashkey  = %s "				
						,
						(			
							user_hashkey,
						)
					)	
				)

