import os
import flask

app = flask.Flask(__name__)
PORT = int(os.getenv("PORT", 8080))

@app.route('/')
def home():
    return "Auto Upload Service is Running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

