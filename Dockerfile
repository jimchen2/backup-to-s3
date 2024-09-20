FROM python:3.9

WORKDIR /app

# Install cron and git
RUN apt-get update && apt-get install -y cron git

# Clone the repository
RUN git clone https://github.com/jimchen2/backup-to-s3.git .

# Install dependencies
RUN pip install -r requirements.txt

# Setup crontab
COPY crontab /etc/cron.d/backup-cron
RUN chmod 0644 /etc/cron.d/backup-cron

# Ensure the cron service will run the job
RUN crontab /etc/cron.d/backup-cron

# Give execution permissions to the Python scripts (just in case)
RUN chmod +x /app/mongo/run.py /app/github/run.py

# Start cron service in the foreground
CMD ["cron", "-f"]
