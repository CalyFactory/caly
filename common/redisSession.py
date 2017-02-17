from uuid import uuid4
from datetime import datetime, timedelta

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from flask import Flask, session, url_for, redirect

import redis
import _pickle as cPickle

#########################################################################################
# This is a session object. It is nothing more than a dict with some extra methods
class RedisSession(CallbackDict, SessionMixin):
	def __init__(self, initial=None, sid=None):
		CallbackDict.__init__(self, initial)
		self.sid = sid
		self.modified = False

#########################################################################################
# Session interface is responsible for handling logic related to sessions
# i.e. storing, saving, etc
class RedisSessionInterface(SessionInterface):
	#====================================================================================
	# Init connection
	def __init__(self, host='localhost', port=6379, db=0, timeout=3600):
		self.store = redis.StrictRedis(host=host, port=port, db=db)
		self.timeout = timeout
	#====================================================================================
	def open_session(self, app, request):
		# Get session id from the cookie
		sid = request.cookies.get(app.session_cookie_name)

		# If id is given (session was created)
		if sid:
			# Try to load a session from Redisdb
			stored_session = None
			ssstr = self.store.get(sid)
			if ssstr:
				stored_session = cPickle.loads(ssstr)
			if stored_session:
				# Check if the session isn't expired
				if stored_session.get('expiration') > datetime.utcnow():
					return RedisSession(initial=stored_session['data'],
										sid=stored_session['sid'])
		
		# If there was no session or it was expired...
		# Generate a random id and create an empty session
		sid = str(uuid4())
		return RedisSession(sid=sid)
	#====================================================================================
	def save_session(self, app, session, response):
		domain = self.get_cookie_domain(app)

		# We're requested to delete the session
		if not session:
			response.delete_cookie(app.session_cookie_name, domain=domain)
			return

		# Refresh the session expiration time
		# First, use get_expiration_time from SessionInterface
		# If it fails, add 1 hour to current time
		if self.get_expiration_time(app, session):
			expiration = self.get_expiration_time(app, session)
		else:
			expiration = datetime.utcnow() + timedelta(hours=87600)

		# Update the Redis document, where sid equals to session.sid
		ssd = {
			'sid': session.sid,
			'data': session,
			'expiration': expiration
		}
		ssstr = cPickle.dumps(ssd)
		self.store.setex(session.sid, self.timeout, ssstr)

		# Refresh the cookie
		response.set_cookie(app.session_cookie_name, session.sid,
							expires=self.get_expiration_time(app, session),
							httponly=True, domain=domain)
