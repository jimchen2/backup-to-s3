FROM python:3.11

WORKDIR /app

# Update package list and install cron and git
RUN apt-get update && apt-get install -y cron git

# Clone the repository
RUN git clone https://github.com/jimchen2/backup-to-s3.git .

# Install dependencies
RUN pip install -r requirements.txt

# Copy crontab file to the cron.d directory
COPY crontab /etc/cron.d/backup-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/backup-cron

# Apply cron job
RUN crontab /etc/cron.d/backup-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
