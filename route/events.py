from manager import db_manager
from flask.views import MethodView
from model import eventModel
from model import userAccountModel
from flask import session
from common.util import utils

import flask

class Events(MethodView):
	def post(self,action):
		if action == 'getList':
			sessionkey = flask.request.form['sessionkey']
			#pageNum = 0 부터 시작된다.
			pageNum = flask.request.form['pageNum']
			user_hashkey = session[sessionkey]
			print('pageNum' + pageNum)
			rangee = 3
			# 0 3 6 9.. 
			pager = int(pageNum) * int(rangee)

			try:
				rows = eventModel.getEvents(user_hashkey,pager,rangee)
			except Exception as e:
				return utils.resErr(str(e))		

			print(rows)
			if len(rows) != 0:
				return utils.resSuccess(rows)
			else:
				return utils.resCustom(201,'Data End')


			# user = userAccountModel.getUserAccount(user_hashkey)


			


