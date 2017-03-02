from common.util import utils
from manager import db_manager

def getNotice():
	return utils.fetch_all_json(
				db_manager.query(
					"SELECT notice_title,notice_description,create_datetime "
					"FROM NOTICE "
					,
					()
				)		
			)		
