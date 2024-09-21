#!/bin/bash


printenv | sed 's/^\(.*\)$/export \1/g' > /app/env.sh

# Set up the cron jobs
echo "0 0 * * 0 . /app/env.sh; /usr/local/bin/python /app/github/run.py >> /var/log/cron.log 2>&1" > /etc/cron.d/backup-cron
echo "*/30 * * * * . /app/env.sh; /usr/local/bin/python /app/mongo/run.py >> /var/log/cron.log 2>&1" >> /etc/cron.d/backup-cron

chmod 0644 /etc/cron.d/backup-cron
crontab /etc/cron.d/backup-cron
cron && tail -f /var/log/cron.log
