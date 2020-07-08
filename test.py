from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/time')
def hello_world():
    return jsonify(time.time())

