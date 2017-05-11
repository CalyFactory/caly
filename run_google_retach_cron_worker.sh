
source ./envCaly/bin/activate &&
celery -A google_retach_cron_worker worker -B -n googleRetachQueue
# celery -A google_retach_cron_worker worker --loglevel=debug -f log/log_google_retach_worker.log -B -n googleRetachQueue

