FROM python:3.11

WORKDIR /app

# Update package list and install cron and git
RUN apt-get update && apt-get install -y cron git

# Clone the repository
RUN git clone https://github.com/jimchen2/backup-to-s3.git .

# Install dependencies
RUN pip install -r requirements.txt

# Make the startup script executable
RUN chmod +x /app/startup.sh

# Create the log file
RUN touch /var/log/cron.log

# Set the startup script as the entry point
CMD ["/app/startup.sh"]
