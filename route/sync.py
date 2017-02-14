from flask.views import MethodView
import flask
from manager.redis import redis


from model import userDeviceModel
from model import userAccountModel
from model import userModel
from model import calendarModel
from common import caldavWrapper

class Sync(MethodView):

	def post(self,action):
		if action == 'sync':
			sessionkey = flask.request.form['sessionkey']
			# redis.set(sessionkey,'cd303e159f5e37a7724e760915b3171ea257445169094a31d31a25c9')
			user_hashkey = redis.get(sessionkey)
			print('hashekuy = >'+str(user_hashkey))

			user = userAccountModel.getUserAccount(user_hashkey)
			print('user'+str(user))
			login_platform = user[0]['login_platform']
			u_id = user[0]['user_id']
			u_pw = user[0]['access_token']
			account_hashkey = user[0]['account_hashkey']
			
			calDavclient = caldavWrapper.getCalDavClient(login_platform,u_id,u_pw)


			calendarModel.setCalendar(calDavclient.getPrincipal().getHomeSet().getCalendars(),account_hashkey)

			return 'hi'
