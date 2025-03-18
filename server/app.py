from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World' 

@app.route('/news-api')
def new_api():
    return 'News end point'

if __name__ == "__main__":
    app.run(debug=True)