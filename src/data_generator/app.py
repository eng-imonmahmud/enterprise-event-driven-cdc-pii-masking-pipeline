import os
import json
import uuid
import random
import datetime
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'CustomerRecords')
table = dynamodb.Table(table_name)

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
DOMAINS = ["example.com", "test.org", "demo.net", "dummy.io"]

def generate_record():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return {
        "user_id": str(uuid.uuid4()),
        "name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}@{random.choice(DOMAINS)}",
        "phone": f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}",
        "signup_date": datetime.datetime.utcnow().isoformat() + "Z",
        "status": random.choice(["ACTIVE", "PENDING", "SUSPENDED"])
    }

def lambda_handler(event, context):
    logger.info("Data generator started.")
    try:
        # Generate 1 to 5 random records per invocation
        num_records = random.randint(1, 5)
        for _ in range(num_records):
            record = generate_record()
            table.put_item(Item=record)
            logger.info(f"Inserted record for user_id: {record['user_id']}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Successfully inserted {num_records} records."})
        }
    except Exception as e:
        logger.error(f"Error generating data: {str(e)}")
        raise e
