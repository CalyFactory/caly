#추천 엔진모듈
import logging
from reco.reco import Reco
from reinforce.reinforce import Reinforce
import extractor.event_extractor 
from datetime import timedelta,datetime
from model import eventModel
from model import recoModel
from common.util.statics import *

def setReco(method,event_hashkey,summary,start_date,end_date,location):
	logging.info("setRECCCCo")
	try:

		if method == "google":
		
			#date만 있는 경우라 시간을 추가해줘야함.
			if(len(start_date)<11):
				start_date = datetime.strptime(start_date, '%Y-%m-%d')
				# start_date = start_date + datetime.timedelta(hours=00,minutes=00)
				start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')

				end_date = datetime.strptime(end_date, '%Y-%m-%d')
				# start_date = start_date + datetime.timedelta(hours=00,minutes=00)
				end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')								
			else:
				start_date = start_date.replace("T"," ")
				end_date = end_date.replace("T"," ")

		else:			
			start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
			end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')								
			# start_date = start_date[:start_date.find('+')]
			# end_date = end_date[:start_date.find('+')]


		if location == None:
			location = "None"


		logging.info("extrcted=>"+str(event_hashkey))
		logging.info("extrcted=>"+str(summary))
		logging.info("extrcted=>"+str(location))	

		logging.info("extrcted=>"+str(start_date))
		logging.info("extrcted=>"+str(end_date))							

		extracted_json = extractor.event_extractor.extract_info_from_event(event_hashkey,summary,start_date,end_date,location)
		
		logging.info("extrcted=>"+str(extracted_json))
		reinforce = Reinforce(extracted_json).event_reco_result
		logging.info("reinforce ->"+str(reinforce))	
		#비추천일경우.. 아무것도 안하면된다.	
		#추천일경우는 1,4,6					
		#eventStauts가 완료됨으로 바꺼준다.
		if reinforce["code"] == RECO_PERFECT or reinforce["code"] == RECO_NO_LOCA_HAS_EVENTTYPE or reinforce["code"] == RECO_HAS_LOCA_NO_EVENTTYPE  : 
			logging.info("success!")
			logging.info("success!" + event_hashkey)
			logging.info("success!" + str(EVENT_RECO_STATUS_SUCCESS))
			logging.info("success!" + str(EVENT_RECO_AUTO))
			# 해당이벤트 성공으로 넣어줌!
			eventModel.updateEventRecoState(event_hashkey,EVENT_RECO_STATUS_SUCCESS)
			# 그리고해당 이벤트는 자동이란것도넣어줌
			eventModel.updateEventRecoMethodState(event_hashkey,EVENT_RECO_AUTO)

			reco = Reco(reinforce["event_info_data"],show_external_data = False)
			logging.info("recos==>"+str(reco.get_reco_list()))
			cafes = reco.get_reco_list()["cafe"]
			restaurants = reco.get_reco_list()["restaurant"]
			places = reco.get_reco_list()["place"]
											
			for idx, cafe in enumerate(cafes):
				recoModel.setEventReco(event_hashkey,cafe["reco_hashkey"],idx)
			
			for idx, restaurant in enumerate(restaurants):									
				recoModel.setEventReco(event_hashkey,restaurant["reco_hashkey"],idx)									
			
			for idx, place in enumerate(places):										
				recoModel.setEventReco(event_hashkey,place["reco_hashkey"],idx)			
	except Exception as e:
		logging.error(str(e))