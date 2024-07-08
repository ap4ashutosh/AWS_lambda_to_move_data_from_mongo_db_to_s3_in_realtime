# MongoDB Atlas to S3 Sync

This project automates the synchronization of data from MongoDB Atlas to Amazon S3, performing an initial full sync and then keeping the S3 bucket updated with any subsequent CRUD operations on the MongoDB collections.

## Prerequisites

- MongoDB Atlas account with a cluster set up
- AWS account with access to Lambda, EventBridge, and S3
- AWS CLI installed and configured
- Python 3.12 installed on your local machine

## Architecture Overview

1. An initial Lambda function performs a full sync of all MongoDB collections to S3.
2. MongoDB Atlas Change Streams detect subsequent changes in the specified collections.
3. A trigger in MongoDB Atlas sends these changes to AWS EventBridge.
4. EventBridge routes the event to another AWS Lambda function.
5. This Lambda function processes the change and updates the corresponding data in S3.

## Setup Process

### 1. Prepare Local Development Environment

1. Create a new directory for your project and navigate to it:

### 2. Create Lambda Functions

#### Full Sync Lambda Function

1. Create `full_sync_lambda.py` with your full sync code.
2. Create the deployment package:

```sh {"id":"01J293PNS9ZG7DYPM4F7Y0403E"}
mkdir python
pip install -r requirements.txt -t python/
cd python
zip -r ../lambda_layer.zip .
cd ..
zip -g lambda_layer.zip full_sync_lambda.py
```

#### Change Sync Lambda Function

1. Create `change_sync_lambda.py` with your change sync code.

2. Add it to the existing deployment package:

```sh {"id":"01J293RDM9S9MEZ4RCEACTPQHG"}
zip -g lambda_layer.zip change_sync_lambda.py
```

### 3. Set Up AWS Lambda

1. Open the AWS Lambda console.

2. Create a Lambda Layer:
   - Navigate to Layers and click "Create layer"
   - Name: "mongodb-s3-sync-layer"
   - Upload the `lambda_layer.zip` file
   - Compatible runtimes: Python 3.12
   - Click "Create"

3. Create Full Sync Lambda Function:
   - Click "Create function"
   - Name: MongoDBToS3FullSync
   - Runtime: Python 3.12
   - Architecture: x86_64
   - Click "Create function"
   - In Configuration, set Handler to `full_sync_lambda.lambda_handler`
   - Add the Layer you created
   - Set appropriate memory and timeout values
   - Configure environment variables (MongoDB connection string, S3 bucket name)

4. Create Change Sync Lambda Function:
   - Repeat the process for a new function named MongoDBToS3ChangeSync
   - Set Handler to `change_sync_lambda.lambda_handler`
   - Add the same Layer
   - Configure similar environment variables

### 4. Set Up IAM Permissions

1. In the AWS IAM console, create a new policy using the JSON in `iam_policy.json` from this repository.

2. Attach this policy to both Lambda function roles.

### 5. Configure MongoDB Atlas

1. Log in to your MongoDB Atlas account.

2. Navigate to your cluster and go to the "Triggers" tab.

3. Click "Add Trigger" and configure a Database Trigger:
   - Trigger Type: Database
   - Name: AtlasToS3Sync
   - Enabled: On
   - Cluster: Select your cluster
   - Database and Collection: Choose your target database and collections
   - Operation Type: Select all (insert, update, replace, delete)
   - Full Document: On
   - Destination: AWS EventBridge
   - AWS Account ID: Enter your AWS Account ID
   - AWS Region: Select the region of your EventBridge

### 6. Set Up AWS EventBridge

1. In the AWS Management Console, go to Amazon EventBridge.

2. Navigate to "Partner event sources" and find the event source created by MongoDB Atlas.

3. Create an Event Bus for this partner event source.

4. Create a Rule in this Event Bus:
   - Name: MongoDBChangeRule
   - Description: Route MongoDB Atlas changes to Lambda
   - Event pattern: Use the pattern in `eventbridge_pattern.json` from this repository
   - Target: Select the MongoDBToS3ChangeSync Lambda function

### 7. Initial Data Sync

1. In the AWS Lambda console, manually run the MongoDBToS3FullSync function to perform the initial full sync of all collections to S3.

### 8. Testing

1. Make changes to your MongoDB Atlas collections.
2. Check the CloudWatch logs for your MongoDBToS3ChangeSync Lambda function.
3. Verify that the corresponding objects in your S3 bucket are being updated correctly.

## Monitoring and Maintenance

- Regularly check CloudWatch logs for both Lambda functions.
- Monitor Lambda performance and adjust configurations as needed.
- Keep track of S3 storage usage and costs.
- Periodically review and update IAM permissions.

## Security Considerations

- Ensure encryption for data in transit and at rest.
- Implement proper access controls for your S3 bucket.
- Regularly rotate AWS and MongoDB Atlas credentials.
- Consider using AWS KMS for additional data encryption.

## Troubleshooting

- For sync issues, check:
  1. MongoDB Atlas trigger configuration
  2. EventBridge partner event source and rule setup
  3. Lambda function logs in CloudWatch
  4. Lambda function permissions
- Ensure all AWS resources are in the same region for optimal performance.

For detailed code implementations, please refer to the corresponding files in this GitHub repository.