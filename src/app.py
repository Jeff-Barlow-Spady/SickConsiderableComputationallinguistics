import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import json_util
import logging

app = Flask(__name__)
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.mydatabase

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET'])
def get_data():
    try:
        data = db.mycollection.find()
        return json_util.dumps(data)
    except Exception as e:
        logging.error(f"Error serializing BSON to JSON: {e}")
        return jsonify({"error": "Failed to serialize data"}), 500

@app.route('/embedded', methods=['GET'])
def get_embedded_data():
    try:
        data = db.mycollection.find({"embedded_field": {"$exists": True}})
        return json_util.dumps(data)
    except Exception as e:
        logging.error(f"Error fetching embedded documents: {e}")
        return jsonify({"error": "Failed to fetch embedded documents"}), 500

if __name__ == '__main__':
    app.run(debug=True)