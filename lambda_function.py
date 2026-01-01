import boto3
import json

def lambda_handler(event, context):
    s3 = boto3.client("s3")
    bucket_name = event["detail"]["bucket"]["name"]
    print(f"Remediating public bucket: {bucket_name}")
  
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
    )
  
    print(f"Block Public Access enabled for {bucket_name}")
    try:
        s3.delete_bucket_policy(Bucket=bucket_name)
        print(f"Public policy deleted from {bucket_name}")
    except Exception as e:
        print(f"No policy to delete or error: {e}")
    
    return {
        "statusCode": 200,
        "body": json.dumps(f"Remediated {bucket_name}")
    }
