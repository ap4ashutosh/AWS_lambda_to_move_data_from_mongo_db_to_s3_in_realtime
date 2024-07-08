import os
import json
import boto3
from pymongo import MongoClient
from botocore.exceptions import ClientError

# MongoDB Atlas connection URI
uri = os.environ.get('MONGODB_URI')

# AWS S3 configuration
s3 = boto3.client('s3',
                  aws_access_key_id=os.environ.get('TG_AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.environ.get('TG_AWS_SECRET_ACCESS_KEY'),
                  region_name=os.environ.get('TG_AWS_REGION'))

# Database name
database_name = 'configurator'

# Function to export data from MongoDB to S3 bucket
def lambda_handler(event, context):
    client = MongoClient(uri)
    try:
        db = client[database_name]
        collections = db.list_collection_names()
        for collection_name in collections:
            collection = db[collection_name]
            data = list(collection.find())
            json_data = json.dumps(data, default=str)  # Convert MongoDB data to JSON
            params = {
                'Bucket': os.environ.get('S3_BUCKET_NAME'),
                'Key': f'{collection_name}.json',
                'Body': json_data
            }
            try:
                s3.put_object(**params)
                print(f"Data from {collection_name} exported to S3 bucket successfully.")
            except ClientError as e:
                print(f"Error exporting data from {collection_name} to S3 bucket: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()