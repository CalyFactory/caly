# Celery configuration file
broker_url = 'amqp://guest:guest@localhost:5672//'
# using serializer name
accept_content = ['json']

# or the actual content-type (MIME)
accept_content = ['application/json']

imports = ('tasks')
