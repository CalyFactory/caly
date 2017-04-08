
source ./envCaly/bin/activate &&
celery -A cron_worker worker --loglevel=debug -f log/log_caldav_worker.log -B -n periodicSyncWorker

