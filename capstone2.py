import streamlit as st
import boto3
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials from environment variables
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_KEY')

# Initialize AWS services with dotenv credentials
try:
    # DynamoDB resource
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    table = dynamodb.Table('hashtag')
    
    # Lambda client
    lambda_client = boto3.client(
        'lambda',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
except (NoCredentialsError, PartialCredentialsError):
    st.error("AWS credentials not configured properly. Please check your AWS setup in the .env file.")

# Streamlit UI
st.title('Social Media Hashtag Trend Analyzer')

# Input for post composition
post_content = st.text_area("Compose your post with hashtags")

# Submit Post
if st.button('Post'):
    if post_content:
        try:
            # Prepare payload for Lambda function
            payload = json.dumps({"post_content": post_content})

            # Invoke AWS Lambda to process post content
            response = lambda_client.invoke(
                FunctionName='SocialMediaHashtagAnalyzer',
                InvocationType='RequestResponse',
                Payload=payload.encode('utf-8')
            )

            # Parse response from Lambda
            lambda_response = json.load(response['Payload'])
            if lambda_response.get("statusCode") == 200:
                st.success("Post submitted successfully!")
            else:
                st.error("Error processing post. Check Lambda logs for more details.")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Post content cannot be empty.")

# Display Trending Hashtags
if st.button('Show Trending Hashtags'):
    try:
        # Scan DynamoDB table for all items (consider using pagination for large datasets)
        response = table.scan()
        items = response.get('Items', [])

        # Count occurrences of each hashtag
        hashtag_counts = {}
        for item in items:
            hashtags = item.get('hashtags', [])
            for hashtag in hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1

        # Sort hashtags by frequency
        sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Display trending hashtags
        st.write("### Trending Hashtags")
        if sorted_hashtags:
            for hashtag, count in sorted_hashtags:
                st.write(f"{hashtag}: {count} times")
        else:
            st.write("No trending hashtags found.")
    
    except Exception as e:
        st.error(f"Error retrieving hashtags: {e}")
