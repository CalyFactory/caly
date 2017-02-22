from route.googleAuth import GoogleAuth
from route.schedule import Schedule
from route.member import Member
from route.sync import Sync
from route.events import Events

def initRoute(app):
	events = Events.as_view('events')	
	app.add_url_rule(
						'/v1.0/events/getList',
						defaults = {'action':'getList'},
						view_func = events, 
						methods = ['POST', ]
					)
	

	sync = Sync.as_view('sync')	
	app.add_url_rule(
						'/v1.0/sync',
						defaults = {'action':'sync'},
						view_func = sync, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/sync/watchReciver',
						defaults = {'action':'watchReciver'},
						view_func = sync, 
						methods = ['POST', ]
					)


	member = Member.as_view('member')
	app.add_url_rule(
						'/v1.0/member/addAccount',
						defaults = {'action':'addAccount'},
						view_func = member, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/member/accountList',
						defaults = {'action':'accountList'},
						view_func = member, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/member/loginCheck',
						defaults = {'action':'loginCheck'},
						view_func = member, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/member/signUp',
						defaults = {'action':'signUp'},
						view_func = member, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/member/registerDevice',
						defaults = {'action':'registerDevice'},
						view_func = member, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/member/updatePushToken',
						defaults = {'action':'updatePushToken'},
						view_func = member, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/member/logout',
						defaults = {'action':'logout'},
						view_func = member, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/member/checkVersion',
						defaults = {'action':'checkVersion'},
						view_func = member, 
						methods = ['POST', ]
					)

	googleAuth = GoogleAuth.as_view('gAuthAPI')
	app.add_url_rule(
						'/', 
						defaults={'action': 'index'},
		                view_func=googleAuth, 
		                methods=['GET', ]
	                )


	app.add_url_rule(
						'/googleAuthCallBack', 
						defaults={'action': 'googleAuthCallBack'},
	                 	view_func=googleAuth, 
	                 	methods=['GET', ]
	                 )

	app.add_url_rule(
						'/calendarSync', 
						defaults={'action': 'calendarSync'},
	                 	view_func=googleAuth, 
	                 	methods=['GET', ]
	                 )
	app.add_url_rule(
						'/googleReceive', 
						defaults={'action': 'googleReceive'},
	                 	view_func=googleAuth, 
	                 	methods=['POST', ]
	                 )

	#schedule라우팅
	schedule = Schedule.as_view('schedule')
	app.add_url_rule(
						'/getCalendarList',
						defaults = {'action':'getCalendarList'},
						view_func = schedule,
						methods=['GET',]
					)
	app.add_url_rule(
						'/setCalendarList',
						defaults = {'action':'setCalendarList'},
						view_func = schedule,
						methods=['GET',]
					)
	app.add_url_rule(
						'/getEvents',
						defaults = {'action':'getEvents'},
						view_func = schedule,
						methods=['GET',]
					)
