import os
import shutil
from datetime import datetime, timedelta, UTC
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ.get('GITHUB_USERNAME')
TOKEN = os.environ.get('GITHUB_TOKEN')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_ENDPOINT = os.environ.get('S3_ENDPOINT')
TEMP_DIR = "./tmp/github_repos"
SHALLOW_BACKUP_PERIOD_DAYS = int(os.environ.get('BACKUP_PERIOD_DAYS', 30))

def backup_github_repos(is_full_backup):
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    s3 = boto3.client('s3',
                      aws_access_key_id=S3_ACCESS_KEY,
                      aws_secret_access_key=S3_SECRET_KEY,
                      endpoint_url=S3_ENDPOINT)

    last_time = datetime.now(UTC) - timedelta(days=31 if is_full_backup else SHALLOW_BACKUP_PERIOD_DAYS)

    headers = {'Authorization': f'token {TOKEN}'}
    repos_url = 'https://api.github.com/user/repos'
    params = {'type': 'all', 'per_page': 100}  # Fetch up to 100 repos per page (maximum allowed by GitHub)
    
    repos = []
    
    # Paginate through all pages of repos
    while repos_url:
        response = requests.get(repos_url, headers=headers, params=params)
        repos.extend(response.json())

        # Get pagination info from the Link header
        if 'Link' in response.headers:
            links = response.headers['Link']
            repos_url = None
            for link in links.split(','):
                if 'rel="next"' in link:
                    repos_url = link[link.find('<') + 1:link.find('>')]
                    break
        else:
            repos_url = None  # No more pages

    # Now we have all repos, filter and process them
    for repo in repos:
        if datetime.strptime(repo['pushed_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC) > last_time:
            archive_url = f"https://github.com/{repo['full_name']}/archive/refs/heads/main.zip"
            archive_response = requests.get(archive_url, headers=headers)
            archive_path = os.path.join(TEMP_DIR, f"{repo['name']}.zip")
            with open(archive_path, 'wb') as f:
                f.write(archive_response.content)

    # Upload to S3
    timestamp = datetime.now().strftime("%Y/%m/%d/%H%M%S")
    for root, dirs, files in os.walk(TEMP_DIR):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, TEMP_DIR)
            s3_key = f"{'full' if is_full_backup else 'shallow'}/{timestamp}/{relative_path}"
            s3.upload_file(local_path, S3_BUCKET, s3_key)

    shutil.rmtree(TEMP_DIR)

    if is_full_backup:
        # Remove shallow backups before creating a full backup
        remove_shallow_backups(s3)

    print(f"GitHub repositories backed up to {S3_BUCKET}/{'full' if is_full_backup else 'shallow'}/{timestamp}/")

def remove_shallow_backups(s3):
    # List all objects in the bucket
    objects = s3.list_objects_v2(Bucket=S3_BUCKET)
    if 'Contents' in objects:
        for obj in objects['Contents']:
            if not obj['Key'].startswith('full/'):
                print(f"Deleting shallow backup: {obj['Key']}")
                s3.delete_object(Bucket=S3_BUCKET, Key=obj['Key'])


def is_full_backup_day():
    # Check if today is within the 1st to the 7th of the month
    today = datetime.now().day
    return 1 <= today <= 8


if __name__ == "__main__":
    full_backup = is_full_backup_day()
    backup_github_repos(full_backup)
