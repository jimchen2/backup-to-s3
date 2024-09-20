FROM python:3.11

WORKDIR /app

# Update package list and install cron and git
RUN apt-get update && apt-get install -y cron git

# Clone the repository
RUN git clone https://github.com/jimchen2/backup-to-s3.git .

# Install dependencies
RUN pip install -r requirements.txt

# Set permissions for crontab file (already in repo)
RUN chmod 0644 crontab

# Apply crontab
RUN crontab crontab

# Ensure cron is running in the foreground
CMD ["cron", "-f"]
