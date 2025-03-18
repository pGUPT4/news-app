from flask import Flask
import requests # for HTTP requests
import os       # for environment variables
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Get the NYT API key from .env
NYT_API_KEY = os.getenv("NYT_API_KEY")

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

@app.route('/')
def hello_world():
    return 'Hello World' 

@app.route('/news-api')
def new_api():
    news_data = get_nyt_news()
    return news_data

if __name__ == "__main__":
    app.run(debug=True)