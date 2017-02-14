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