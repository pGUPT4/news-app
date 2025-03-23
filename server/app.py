from flask import Flask, jsonify
from flask_cors import CORS
import pymongo
import requests
import os
import json
from datetime import datetime
import boto3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

env_vars = {
    "MONGO_URI": os.getenv("MONGO_URI"),
    "NYT_API_KEY": os.getenv("NYT_API_KEY"),
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "AWS_BUCKET_NAME": os.getenv("AWS_BUCKET_NAME", "pgupt4-news-app-s3")
}

# Validate env vars
for key, value in env_vars.items():
    if not value:
        logger.error(f"Missing env var: {key}")
        raise ValueError(f"{key} not set")

client = None
try:
    client = pymongo.MongoClient(env_vars["MONGO_URI"])
    db = client['news_app']
    users_collection = db['users']
    logger.info("MongoDB connected successfully")
except Exception as e:
    logger.error(f"MongoDB connection failed: {str(e)}")

s3 = None
try:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=env_vars["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=env_vars["AWS_SECRET_ACCESS_KEY"]
    )
    logger.info("S3 client initialized")
except Exception as e:
    logger.error(f"S3 client init failed: {str(e)}")

NYT_API_KEY = env_vars["NYT_API_KEY"]

def get_nyt_news():
    url = "http://api.nytimes.com/svc/news/v3/content/all/all.json"
    params = {"api-key": NYT_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()["results"]
    except requests.RequestException as e:
        logger.error(f"NYT API request failed: {str(e)}")
        return {"error": str(e)}

def upload_to_s3(data, bucket_name=env_vars["AWS_BUCKET_NAME"], key_prefix="raw"):
    if not s3:
        return {"status": "error", "message": "S3 client not initialized"}
    key = f"{key_prefix}/news-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
    try:
        s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(data), ContentType="application/json")
        return {"status": "success", "key": key}
    except Exception as e:
        logger.error(f"S3 upload failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def get_from_s3(bucket_name=env_vars["AWS_BUCKET_NAME"], key_prefix="processed"):
    if not s3:
        return {"error": "S3 client not initialized"}
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=key_prefix)
        if "Contents" not in response:
            return {"error": "No processed files found"}
        latest_key = max(response["Contents"], key=lambda x: x["LastModified"])["Key"]
        obj = s3.get_object(Bucket=bucket_name, Key=latest_key)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except Exception as e:
        logger.error(f"S3 fetch failed: {str(e)}")
        return {"error": str(e)}

@app.route('/raw')
def hello_world():
    return jsonify(get_nyt_news())

@app.route('/news-galore')
def news_galore():
    news_data = get_nyt_news()
    upload_result = upload_to_s3(news_data)
    if upload_result["status"] != "success":
        return jsonify({"error": upload_result["message"]}), 500
    processed_data = get_from_s3()
    if "error" not in processed_data:
        return jsonify(processed_data)
    return jsonify({"message": f"Uploaded to S3 at {upload_result['key']}", "fetch_error": processed_data["error"]})

@app.route('/mongo')
def mongo():
    if not client:
        return jsonify({'error': 'MongoDB not connected'}), 500
    try:
        users_collection.insert_one({'email': 'test@example.com'})
        return jsonify({'message': 'MongoDB Atlas connected and test user added'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# from flask import Flask, jsonify
# from flask_cors import CORS
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app)

# @app.route('/news-galore')
# def news_galore():
#     logger.info("Serving /news-galore")
#     return jsonify({"news": "Test from Heroku"})

# @app.route('/')
# def health_check():
#     return jsonify({"status": "ok"}), 200

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)