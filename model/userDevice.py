from common.util import utils
from manager import db_manager

def getUserDevice(sessionkey):
	return utils.fetch_all_json(
			db_manager.query(
					"SELECT * FROM USERDEVICE WHERE session_key = %s "
					,
					(sessionkey,) 						
			)
		)