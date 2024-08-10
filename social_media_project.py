import streamlit as st
import boto3
import json
from boto3.dynamodb.conditions import Key
from datetime import datetime

# Explicit AWS credentials (Replace with your actual credentials)
AWS_REGION = 'ap-south-1'
AWS_ACCESS_KEY_ID = '********'
AWS_SECRET_ACCESS_KEY = '*********************'

# Initialize DynamoDB with explicit credentials
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
table = dynamodb.Table('hashtag')

# Streamlit UI
st.title('Social Media Hashtag Trend Analyzer')

# Input for post composition
post_content = st.text_area("Compose your post with hashtags")

if st.button('Post'):
    if post_content:
        # Properly format the post content as JSON
        payload = json.dumps({"post_content": post_content})

        # Send post content to AWS Lambda with explicit credentials
        lambda_client = boto3.client(
            'lambda',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        response = lambda_client.invoke(
            FunctionName='your-lambda-function-name',
            InvocationType='RequestResponse',
            Payload=payload.encode('utf-8')
        )
        st.success("Post submitted successfully!")
    else:
        st.error("Post content cannot be empty.")

# Display Trending Hashtags
if st.button('Show Trending Hashtags'):
    response = table.scan()
    items = response['Items']
    
    hashtag_counts = {}
    for item in items:
        hashtags = item.get('hashtags', [])
        for hashtag in hashtags:
            hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1

    sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    st.write("### Trending Hashtags")
    for hashtag, count in sorted_hashtags:
        st.write(f"{hashtag}: {count} times")

# Real-time update of trending hashtags (optional)
st.button('Refresh')
