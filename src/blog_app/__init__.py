from flask import Flask,request,jsonify
from pymongo import MongoClient
import json
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timezone
from bson import ObjectId

app=Flask(__name__)
mongo_url = MongoClient('mongodb+srv://guffranjgshaik_db_user:zFMHm7NoVSVvHUky@studentattendance.u8cdbrl.mongodb.net/?appName=StudentAttendance')
mongo_client = mongo_url["blog_app"]
users = mongo_client["users"]
app.config["JWT_SECRET_KEY"]="secret-key"

jwt=JWTManager(app)
users=mongo.db.users
blogs=mongo.db.blogs

@app.post("/register")
def register_user():
    data = request.get_json()
    user = users.find_one({"email":data["email"]})
    if user:
        return"user already exists"
    user_data = {}
    for p in data:
        user_data = {
            "name" : p["name"],
            "email" : p["email"],
            "password" : p ["password"]
        }
    users.insert_one(user_data)
    return "Student added"

@app.post("/login")
def login():
    data=request.get_json() or {}
    token=create_access_token(identity=str(user["_id"]))
    return {
        "message":"Login successful",
        "token":token
    },200

@app.post("/blogs")
@jwt_required()
def create_blog():
    data=request.get_json() or {}

    if not data.get("title") or not data.get("content"):
        return {"error":"Title and content are required"},400

    current_user=get_jwt_identity()

    blog={
        "title":data["title"].strip(),
        "content":data["content"].strip(),
        "author_id":ObjectId(current_user),
        "status":"draft",
        "created_at":now(),
        "updated_at":now(),
        "published_at":None
    }

    result=blogs.insert_one(blog)
    blog["_id"]=result.inserted_id

    return {
        "message":"Blog created",
        "blog":blog_data(blog)
    },201

@app.get("/blogs")
def get_blogs():
    result=blogs.find({"status":"published"}).sort("published_at",-1)

    return {
        "blogs":[blog_data(blog) for blog in result]
    },200

if __name__=="__main__":
    app.run(debug=True)
