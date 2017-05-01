from route.member import Member
from route.sync import Sync
from route.events import Events
from route.setting import Setting
from route.reco import Reco
from route.support import Support

def initRoute(app):
	support = Support.as_view('support')
	app.add_url_rule(
						'/v1.0/support/notices',
						defaults = {'action':'notices'},
						view_func = support, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/support/requests',
						defaults = {'action':'requests'},
						view_func = support, 
						methods = ['POST', ]
					)	

	reco = Reco.as_view('reco')
	app.add_url_rule(
						'/v1.0/reco/getList',
						defaults = {'action':'getList'},
						view_func = reco, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/reco/tracking',
						defaults = {'action':'tracking'},
						view_func = reco, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/reco/checkRecoState',
						defaults = {'action':'checkRecoState'},
						view_func = reco, 
						methods = ['POST', ]
					)	

	app.add_url_rule(
						'/v1.0/reco/setLog',
						defaults = {'action':'setLog'},
						view_func = reco, 
						methods = ['POST', ]
					)	
	setting = Setting.as_view('setting')
	app.add_url_rule(
						'/v1.0/setting/updatePushToken',
						defaults = {'action':'updatePushToken'},
						view_func = setting, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/setting/setReceivePush',
						defaults = {'action':'setReceivePush'},
						view_func = setting, 
						methods = ['POST', ]
					)


	events = Events.as_view('events')	
	app.add_url_rule(
						'/v1.0/events/getList',
						defaults = {'action':'getList'},
						view_func = events, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/events/setLog',
						defaults = {'action':'setLog'},
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
	app.add_url_rule(
						'/v1.0/checkSync',
						defaults = {'action':'checkSync'},
						view_func = sync, 
						methods = ['POST', ]
					)
	app.add_url_rule(
						'/v1.0/sync/caldavManualSync',
						defaults = {'action':'caldavManualSync'},
						view_func = sync, 
						methods = ['POST', ]
					)

# withdrawal
	member = Member.as_view('member')
	app.add_url_rule(
						'/v1.0/member/removeAccount',
						defaults = {'action':'removeAccount'},
						view_func = member, 
						methods = ['POST', ]
					)
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
	app.add_url_rule(
						'/v1.0/member/withdrawal',
						defaults = {'action':'withdrawal'},
						view_func = member, 
						methods = ['POST', ]
					)	
	app.add_url_rule(
						'/v1.0/member/updateAccount',
						defaults = {'action':'updateAccount'},
						view_func = member, 
						methods = ['POST', ]
					)		

