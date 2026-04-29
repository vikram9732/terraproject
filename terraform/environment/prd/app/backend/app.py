from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import boto3
import os
import uuid
import json

app = Flask(__name__)
CORS(app)

# MongoDB URL from environment
mongo_url = os.getenv("MONGO_URL")
mongo_db_name = os.getenv("MONGO_DB_NAME", "clickops-db-dev")

import os
from pymongo import MongoClient

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo-container:27017/")
db_name = os.getenv("MONGO_DB_NAME", "clickops-db-dev")

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db["users"]

# AWS / S3
s3_bucket = os.getenv("S3_BUCKET_NAME")
aws_region = os.getenv("AWS_REGION", "ap-south-1")

s3_client = boto3.client("s3", region_name=aws_region)

@app.route("/")
def home():
    return "ClickOps backend is running!"

@app.route("/submit", methods=["POST"])
def submit():
    try:
        name = request.form.get("name")
        age = request.form.get("age")
        picture = request.files.get("picture")

        if not name or not age or not picture:
            return jsonify({"error": "Name, age, and picture are required"}), 400

        file_extension = picture.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        s3_client.upload_fileobj(
            picture,
            s3_bucket,
            unique_filename,
            ExtraArgs={"ContentType": picture.content_type}
        )

        image_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{unique_filename}"

        document = {
            "name": name,
            "age": int(age),
            "picture_url": image_url
        }

        result = collection.insert_one(document)

        # 🔥 FIX HERE
        document["_id"] = str(result.inserted_id)

        return jsonify({
            "message": "Data inserted successfully",
            "data": document
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/view", methods=["GET"])
def view():
    data = []
    for item in collection.find({}):
        item["_id"] = str(item["_id"])
        data.append(item)
    return jsonify({"data": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)