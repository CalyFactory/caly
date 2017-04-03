source ./envCaly/bin/activate &&
celery -A cron_worker worker --beat -n periodicSyncWorker -Q periodicSyncQueue
