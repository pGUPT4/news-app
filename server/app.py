from flask import Flask
import requests # for HTTP requests
import os       # for environment variables
from dotenv import load_dotenv
import json

from datetime import datetime

import boto3

load_dotenv()

app = Flask(__name__)

# Get the NYT API key from .env
NYT_API_KEY = os.getenv("NYT_API_KEY")

s3 =boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Function to fetch news from NYT Times Wire API
def get_nyt_news():
    url = "http://api.nytimes.com/svc/news/v3/content/all/all.json"
    params = {"api-key": NYT_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an error for bad responses (e.g., 404, 403)
        data = response.json()
        return data["results"]  # Return the list of news items
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # Return error message if the request fails

# Function to upload news data to S3
def upload_to_s3(data, bucket_name=os.getenv('AWS_BUCKET_NAME'), key_prefix="raw"):
    # Generate a unique key
    key = f"{key_prefix}/news-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
    
    # Convert data to JSON string and upload
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        return {"status": "success", "key": key}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_from_s3(bucket_name="pgupt4-news-app-s3", key_prefix="processed"):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=key_prefix)
        if "Contents" not in response:
            return {"error": "No processed files found"}
        latest_key = max(response["Contents"], key=lambda x: x["LastModified"])["Key"]
        obj = s3.get_object(Bucket=bucket_name, Key=latest_key)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def hello_world():
    return 'Hello World' 

@app.route('/news-galore')
def news_galore():
    news_data = get_nyt_news()

    upload_result = upload_to_s3(news_data)

    if upload_result["status"] != "success":
        return {"error": upload_result["message"]}
    
    # Fetch processed data from S3 (after Lambda runs)
    processed_data = get_from_s3()
    if "error" not in processed_data:
        return processed_data
    else:
        return {"message": f"Uploaded to S3 at {upload_result['key']}", "fetch_error": processed_data["error"]}

    # return news_data

if __name__ == "__main__":
    app.run(debug=True)