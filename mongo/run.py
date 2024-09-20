import os
import boto3
from pymongo import MongoClient
from bson.json_util import dumps
from datetime import datetime, timedelta
from pymongo.errors import OperationFailure
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def backup_mongodb_to_s3():
    # Get environment variables
    mongo_uri = os.getenv('MONGO_MONGODB_URI')
    s3_bucket = os.getenv('MONGO_S3_BUCKET_NAME')
    aws_access_key = os.getenv('MONGO_AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('MONGO_AWS_SECRET_ACCESS_KEY')
    aws_endpoint = os.getenv('MONGO_AWS_S3_ENDPOINT')  
    
    backup_file = "./tmp/mongodb_backup.json"
    os.makedirs(os.path.dirname(backup_file), exist_ok=True)

    # MongoDB backup
    client = MongoClient(mongo_uri)
    with open(backup_file, 'w') as f:
        for db in client.list_database_names():
            if db not in ['admin', 'local', 'config']:  # Skip system databases
                for collection in client[db].list_collection_names():
                    try:
                        f.write(f"Database: {db}, Collection: {collection}\n")
                        f.write(dumps(client[db][collection].find()) + "\n")
                    except OperationFailure as e:
                        f.write(f"Error accessing {db}.{collection}: {str(e)}\n")
    
    # Upload to S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        endpoint_url=aws_endpoint
    )
    
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y/%m/%d/%H%M%S")
    
    # Check if time is between 00:00 and 01:00
    is_full_backup = current_time.hour == 0
    if is_full_backup:
        s3_key = f"full/{timestamp}/backup.json"
    else:
        s3_key = f"{timestamp}/backup.json"
    
    s3.upload_file(
        backup_file, 
        s3_bucket, 
        s3_key,
    )
    
    # Remove old shallow backups only during full backup
    if is_full_backup:
        remove_old_backups(s3, s3_bucket)
    
    return f"Backup uploaded to {s3_bucket}/{s3_key}"

def remove_old_backups(s3, bucket_name):
    # List objects in the bucket
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name)

    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            if not key.startswith('full/'):
                s3.delete_object(Bucket=bucket_name, Key=key)
                print(f"Deleted shallow backup: {key}")

if __name__ == "__main__":
    result = backup_mongodb_to_s3()
    print(result)
