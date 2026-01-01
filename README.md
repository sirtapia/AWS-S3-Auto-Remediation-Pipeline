# AWS-S3-Auto-Remediation-Pipeline
Automated security remediation system that detects and fixes public S3 buckets in near real-time using AWS Lambda, EventBridge, and CloudTrail.

## Components

| Component | Purpose |
|-----------|---------|
| **Lambda Function** | Remediates public buckets by enabling Block Public Access and deleting public policies |
| **IAM Role** | Grants Lambda permissions to modify S3 buckets and write logs |
| **EventBridge Rule** | Triggers Lambda when S3 policy changes are detected |
| **CloudTrail** | Logs S3 API calls and sends events to EventBridge |

## Files

- `lambda_function.py` - Lambda function code (Python 3.12)
- `trust-policy.json` - IAM trust policy allowing Lambda to assume the role
- `event-pattern.json` - EventBridge rule pattern for S3 events
- `targets.json` - EventBridge target configuration
- `cloudtrail-bucket-policy.json` - S3 bucket policy for CloudTrail logs
- `test-event.json` - Sample event for testing Lambda locally


### Prereqs
- AWS CLI 
- AWS account 

### Step 1: Create IAM Role

```bash
aws iam create-role --role-name S3RemediationLambdaRole --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy --role-name S3RemediationLambdaRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy --role-name S3RemediationLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### Step 2: Deploy Lambda Function

```bash
zip lambda_function.zip lambda_function.py

aws lambda create-function \
  --function-name S3PublicBucketRemediation \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/S3RemediationLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 30
```

### Step 3: Create CloudTrail

```bash
aws s3api create-bucket --bucket your-cloudtrail-logs-bucket --region us-east-2 --create-bucket-configuration LocationConstraint=us-east-2

aws s3api put-bucket-policy --bucket your-cloudtrail-logs-bucket --policy file://cloudtrail-bucket-policy.json

aws cloudtrail create-trail --name S3SecurityTrail --s3-bucket-name your-cloudtrail-logs-bucket

aws cloudtrail start-logging --name S3SecurityTrail
```

### Step 4: Create EventBridge Rule

```bash
aws events put-rule --name S3PublicBucketRule --event-pattern file://event-pattern.json

aws lambda add-permission \
  --function-name S3PublicBucketRemediation \
  --statement-id EventBridgeInvoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-2:YOUR_ACCOUNT_ID:rule/S3PublicBucketRule

aws events put-targets --rule S3PublicBucketRule --targets file://targets.json
```

## Test

```bash
aws lambda invoke \
  --function-name S3PublicBucketRemediation \
  --payload fileb://test-event.json \
  output.json

cat output.json
```

### End-to-End Test

1. Create a test S3 bucket
2. Disable Block Public Access
3. Apply a public bucket policy
4. Wait 5-15 minutes for CloudTrail to deliver events
5. Verify the bucket was remediated

## Cleanup

```bash
aws lambda delete-function --function-name S3PublicBucketRemediation
aws events remove-targets --rule S3PublicBucketRule --ids "1"
aws events delete-rule --name S3PublicBucketRule
aws cloudtrail delete-trail --name S3SecurityTrail
aws s3 rb s3://your-cloudtrail-logs-bucket --force
aws iam detach-role-policy --role-name S3RemediationLambdaRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam detach-role-policy --role-name S3RemediationLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name S3RemediationLambdaRole
```

## Author:
- GitHub: [@sirtapia](https://github.com/sirtapia)
- Email: cristian.tapiavalenz@gmail.com
- LinkedIn: [Cristian Tapia](https://www.linkedin.com/in/cristian-tapia-076a84326/)
