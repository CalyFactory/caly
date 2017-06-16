#!/bin/bash
argv1=$1

bash run_reco_sys.sh

# SERVER=$(ps -ef | grep '/home/yenos/caly/envCaly/bin/gunicorn -w 9 -b 0.0.0.0:55566 caly:app'| wc -l) 
SERVER=$(ps -ef | grep ' 0.0.0.0:55566 caly:app'| wc -l) 

if [ $SERVER -ge 3 ]
then
	echo existServer
	# pkill -9 -ef 'home/yenos/caly/envCaly/bin/gunicorn -w 9 -b 0.0.0.0:55566 caly:app'
	pkill -9 -ef ' 0.0.0.0:55566 caly:app'
fi	
nohup bash run_caly.sh &> /dev/null &

# WORKER=$(ps -ef | grep '/home/yenos/caly/envCaly/bin/celery -A sync_worker worker --loglevel=debug -f log/log_sync_worker.log' | wc -l) 
WORKER=$(ps -ef | grep ' -A sync_worker' | wc -l) 
if [ $WORKER -ge 3 ]
then
	echo existCelery
	if [ $argv1 == "withCelery" ] || [ $argv1 == "all" ]
		then
			echo reStartCelery
			# pkill -9 -ef '/home/yenos/caly/envCaly/bin/celery -A sync_worker worker --loglevel=debug -f log/log_sync_worker.log'
			pkill -9 -ef ' -A sync_worker worker'
			nohup bash run_worker.sh &> /dev/null &	
	fi
else
	echo firstCelery
	nohup bash run_worker.sh &> /dev/null &	
fi	

# CALDAV_WORKER=$(ps -ef | grep '/home/yenos/caly/envCaly/bin/celery -A cron_worker worker --loglevel=debug -f log/log_caldav_worker.log -B -n periodicSyncWorker' | wc -l) 
CALDAV_WORKER=$(ps -ef | grep ' -A cron_worker worker' | wc -l) 
echo CALDAV_WORKER
if [ $CALDAV_WORKER -ge 3 ]
then
	echo first caldavworker
	if [ $argv1 == "withCaldavWorker" ] || [ $argv1 == "all" ]
		then
			echo registCaldav
			# pkill -9 -ef '/home/yenos/caly/envCaly/bin/celery -A cron_worker worker --loglevel=debug -f log/log_caldav_worker.log -B -n periodicSyncWorker'
			pkill -9 -ef ' -A cron_worker worker'
			nohup bash run_caldav_worker.sh &> /dev/null &	
	fi
else
	echo first caldavworker
	nohup bash run_caldav_worker.sh &> /dev/null &
fi	


# GOOGLE_RETACH=$(ps -ef | grep '/home/yenos/caly/envCaly/bin/celery -A google_retach_cron_worker worker --loglevel=debug -f log/log_google_retach_worker.log -B -n googleRetachQueue' | wc -l) 
GOOGLE_RETACH=$(ps -ef | grep ' -A google_retach_cron_worker worker' | wc -l) 
if [ $GOOGLE_RETACH -ge 3 ]
then
	echo  GOOGLE_RETACH
	if [ $argv1 == "withGoogleRetachWorker" ] || [ $argv1 == "all" ]
		then
			echo registGOOGLE_RETACH
			# pkill -9 -ef '/home/yenos/caly/envCaly/bin/celery -A google_retach_cron_worker worker --loglevel=debug -f log/log_google_retach_worker.log -B -n googleRetachQueue'
			pkill -9 -ef ' -A google_retach_cron_worker worker'
			nohup bash run_google_retach_cron_worker.sh &> /dev/null &	
	fi
else
	echo first GOOGLE_RETACH
	nohup bash run_google_retach_cron_worker.sh &> /dev/null &
fi	

DAILYJOB=$(ps -ef | grep 'run_dailyJob.sh' | wc -l)
if [ $DAILYJOB -ge 2 ]
then
	echo  DAILYJOB
	if [ $argv1 == "withDailyJob" ] || [ $argv1 == "all" ]
		then
			echo registDAILYJOB	
			pkill -9 -ef 'dailyCron.py'
			nohup bash run_dailyJob.sh &> /dev/null &
	fi
else
	echo first DAILYJOB
	nohup bash run_dailyJob.sh &> /dev/null &
fi	


