from common.util import utils
from manager import db_manager
#sync	
#푸시등록요청한것들 찾기
def getRecoList(event_hashkey,category):
	return utils.fetch_all_json(
				db_manager.query(
						"SELECT RECO_HASHTAG.reco_hashkey, RECOMMENDATION.region, "
						"EVENT_RECO.event_hashkey, "
						"RECOMMENDATION.category, RECOMMENDATION.title, "						
						"RECOMMENDATION.img_url,RECOMMENDATION.price, "
						"RECOMMENDATION.map_url,RECOMMENDATION.deep_url, "					
						"GROUP_CONCAT(HASHTAG.tag_name  order by HASHTAG.tag_name asc SEPARATOR ', ') as tagNames "
						"FROM RECO_HASHTAG "
						"LEFT JOIN HASHTAG on RECO_HASHTAG.hash_code = HASHTAG.code "
						"LEFT JOIN RECOMMENDATION on RECOMMENDATION.reco_hashkey = RECO_HASHTAG.reco_hashkey "
						"LEFT JOIN EVENT_RECO on EVENT_RECO.reco_hashkey = RECOMMENDATION.reco_hashkey "
						"WHERE  EVENT_RECO.event_hashkey = %s and category = %s "
						"GROUP BY reco_hashkey "						
						,
						(event_hashkey,category) 						
				)
			)


def trackingReco(apikey,reco_hashkey,event_hashkey,account_hashkey,typee):
	return db_manager.query(
					"INSERT INTO RECO_TRACKER "
					"(apikey,reco_hashkey,event_hashkey,account_hashkey,type) "
					"values "
					"(%s,%s,%s,%s,%s)"
					,
					(apikey,reco_hashkey,event_hashkey,account_hashkey,typee)
			)
	
