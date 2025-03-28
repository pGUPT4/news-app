from flask import Flask, jsonify, request, session, redirect
from flask_cors import CORS
import pymongo
import requests
import os
import json
from datetime import datetime
import boto3
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

load_dotenv()  # Load .env file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "temp-secret")

# Google OAuth Config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "https://news-recommender-backend-20d530136c15.herokuapp.com/auth/google/callback"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPES = ["openid", "email", "profile"]

env_vars = {
    "MONGO_URI": os.getenv("MONGO_URI"),
    "NYT_API_KEY": os.getenv("NYT_API_KEY"),
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "AWS_BUCKET_NAME": os.getenv("AWS_BUCKET_NAME", "pgupt4-news-app-s3")
}

for key, value in env_vars.items():
    if not value:
        logger.error(f"Missing env var: {key}")
        raise ValueError(f"{key} not set")

# MongoDB
client = pymongo.MongoClient(env_vars["MONGO_URI"])
db = client['news_app']
users_collection = db['users']
logger.info("MongoDB connected")

# S3
s3 = boto3.client(
    "s3",
    aws_access_key_id=env_vars["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=env_vars["AWS_SECRET_ACCESS_KEY"]
)

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
    key = f"{key_prefix}/news-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
    s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(data), ContentType="application/json")
    return {"status": "success", "key": key}

def get_from_s3(bucket_name=env_vars["AWS_BUCKET_NAME"], key_prefix="processed"):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=key_prefix)
    if "Contents" not in response:
        return {"error": "No processed files found"}
    latest_key = max(response["Contents"], key=lambda x: x["LastModified"])["Key"]
    obj = s3.get_object(Bucket=bucket_name, Key=latest_key)
    return json.loads(obj["Body"].read().decode("utf-8"))

def get_google_oauth():
    return OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=GOOGLE_REDIRECT_URI, scope=SCOPES)

# Old Login Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    if users_collection.find_one({"username": username}):
        return jsonify({"error": "Username taken"}), 409
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password})
    return jsonify({"message": "User registered"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        session['username'] = username
        return jsonify({"message": "Logged in"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# OAuth Routes
@app.route('/auth/google')
def google_login():
    google = get_google_oauth()
    auth_url, state = google.authorization_url(GOOGLE_AUTH_URL, access_type="offline")
    session['oauth_state'] = state
    return redirect(auth_url)

@app.route('/auth/google/callback')
def google_callback():
    google = get_google_oauth()
    token = google.fetch_token(
        GOOGLE_TOKEN_URL,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=request.url
    )
    session['oauth_token'] = token
    user_info = google.get(GOOGLE_USERINFO_URL).json()
    session['user_id'] = user_info['sub']
    users_collection.update_one(
        {"sub": user_info['sub']},
        {"$set": {"email": user_info['email'], "name": user_info['name']}},
        upsert=True
    )
    return redirect("https://my-4wq0uveaw-parth-guptas-projects-847e8d83.vercel.app/")  # Home

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('oauth_token', None)
    session.pop('user_id', None)
    return jsonify({"message": "Logged out"}), 200

@app.route('/raw')
def hello_world():
    return jsonify(get_nyt_news())

@app.route('/news-galore')
def news_galore():
    if 'username' not in session and 'user_id' not in session:  # Check both
        return jsonify({"error": "Login required"}), 401
    news_data = get_nyt_news()
    upload_result = upload_to_s3(news_data)
    if upload_result["status"] != "success":
        return jsonify({"error": upload_result["message"]}), 500
    processed_data = get_from_s3()
    if "error" not in processed_data:
        return jsonify(processed_data)
    return jsonify(news_data)  # Fallback to raw news

@app.route('/')
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)