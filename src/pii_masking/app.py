import os
import json
import logging
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
bucket_name = os.environ.get('S3_BUCKET_NAME')

def mask_email(email):
    if not email or '@' not in email:
        return email
    parts = email.split('@')
    name = parts[0]
    domain = parts[1]
    if len(name) <= 2:
        masked_name = '*' * len(name)
    else:
        masked_name = name[0] + '*' * (len(name) - 2) + name[-1]
    return f"{masked_name}@{domain}"

def mask_phone(phone):
    if not phone or len(phone) < 4:
        return phone
    # Mask all but the last 4 characters
    return '*' * (len(phone) - 4) + phone[-4:]

def unmarshal_dynamodb_json(node):
    # A simple unmarshaller for DynamoDB types
    if not isinstance(node, dict):
        return node
    for key, value in node.items():
        if key == 'S': return value
        if key == 'N': return float(value) if '.' in value else int(value)
        if key == 'BOOL': return value
        if key == 'M': return {k: unmarshal_dynamodb_json(v) for k, v in value.items()}
        if key == 'L': return [unmarshal_dynamodb_json(v) for v in value]
    return node

def lambda_handler(event, context):
    logger.info(f"Received {len(event['Records'])} records from DynamoDB stream.")
    
    masked_records = []
    
    for record in event['Records']:
        event_name = record['eventName']
        
        # Only process INSERT and MODIFY events
        if event_name in ['INSERT', 'MODIFY']:
            new_image = record['dynamodb'].get('NewImage', {})
            
            # Convert DynamoDB JSON to standard Python dict
            item = {k: unmarshal_dynamodb_json(v) for k, v in new_image.items()}
            
            # Mask PII
            if 'email' in item:
                item['email'] = mask_email(item['email'])
            if 'phone' in item:
                item['phone'] = mask_phone(item['phone'])
                
            masked_records.append(item)
            logger.info(f"Masked record for user_id: {item.get('user_id')}")
            
    if masked_records:
        try:
            # Group records by line (JSON lines)
            json_lines = "\n".join([json.dumps(r) for r in masked_records])
            
            # Create a unique filename based on timestamp
            timestamp = datetime.utcnow().strftime('%Y/%m/%d/%H-%M-%S-%f')
            file_key = f"masked_data/{timestamp}.json"
            
            # Upload to S3
            s3.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=json_lines,
                ContentType='application/json'
            )
            logger.info(f"Successfully uploaded {len(masked_records)} records to s3://{bucket_name}/{file_key}")
            
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise e
            
    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Processed {len(masked_records)} records."})
    }
