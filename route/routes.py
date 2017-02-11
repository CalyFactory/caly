from route.googleAuth import GoogleAuth
from route.schedule import Schedule
from route.member import Member

def initRoute(app):
	member = Member.as_view('member')
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
