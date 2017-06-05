
source envCaly/bin/activate && NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn -w $(( `cat /proc/cpuinfo | grep 'core id' | wc -l` + 1 )) -b 0.0.0.0:55566 caly:app 