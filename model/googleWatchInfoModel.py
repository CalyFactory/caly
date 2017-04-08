from common.util import utils
from manager import db_manager


def setGoogleWatchInfo(channel_id,type):
	return	db_manager.query(
				"""
				INSERT INTO GOOGLE_WATCH_INFO (channel_id,type)
				VALUES(%s,%s)
				"""
				,
				(channel_id,type)
			)		
					

