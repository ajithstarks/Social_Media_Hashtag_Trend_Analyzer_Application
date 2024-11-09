import json
import re
import uuid
import boto3
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('hashtag')  # Replace with your DynamoDB table name

def lambda_handler(event, context):
    try:
        # Parse post content from event
        post_content = event.get("post_content", "")
        if not post_content:
            return {
                "statusCode": 400,
                "body": json.dumps("Post content is empty.")
            }
        
        # Generate unique post ID
        post_id = str(uuid.uuid4())

        # Extract hashtags
        hashtags = re.findall(r"#(\w+)", post_content)

        # Create timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Item for DynamoDB
        item = {
            'post_id': post_id,
            'post_content': post_content,
            'hashtags': hashtags,
            'timestamp': timestamp
        }

        # Store item in DynamoDB
        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps("Post successfully stored.")
        }
    
    except Exception as e:
        # Log error and return error response
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps("An error occurred while processing the post.")
        }
