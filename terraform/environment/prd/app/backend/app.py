from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import boto3
import os
import uuid
import json

app = Flask(__name__)
CORS(app)

aws_region = os.getenv("AWS_REGION", "ap-south-1")
secret_name = os.getenv("SECRET_NAME", "clickops-sm-dev")


def get_secret():
    client = boto3.client("secretsmanager", region_name=aws_region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


try:
    secret = get_secret()

    mongo_uri = secret.get("MONGO_URL", "mongodb://mongo-container:27017/")
    db_name = secret.get("MONGO_DB_NAME", "clickops-db-dev")
    s3_bucket = secret.get("S3_BUCKET_NAME")
    aws_region = secret.get("AWS_REGION", aws_region)

except Exception:
    mongo_uri = os.getenv("MONGO_URL") or os.getenv("MONGO_URI", "mongodb://mongo-container:27017/")
    db_name = os.getenv("MONGO_DB_NAME", "clickops-db-dev")
    s3_bucket = os.getenv("S3_BUCKET_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db["users"]

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

        if not s3_bucket:
            return jsonify({"error": "S3_BUCKET_NAME is missing"}), 500

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
        document["_id"] = str(result.inserted_id)

        return jsonify({
            "message": "Data inserted successfully",
            "data": document
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/view", methods=["GET"])
def view():
    try:
        data = []
        for item in collection.find({}):
            item["_id"] = str(item["_id"])
            data.append(item)

        return jsonify({"data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "secret_name": secret_name,
        "mongo_db": db_name,
        "s3_bucket": s3_bucket
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)