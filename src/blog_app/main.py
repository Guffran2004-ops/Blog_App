from flask import Flask,request
from flask_jwt_extended import create_access_token,JWTManager,jwt_required,get_jwt_identity
from werkzeug.security import generate_password_hash,check_password_hash
from uuid import uuid4
from .database import users,blogs
from .blogs import blogs_bp

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "dsbvnhsbjsbnksjdvkljvisjldsj"
jwt = JWTManager(app)
app.register_blueprint(blogs_bp)

@app.route("/register", methods=["POST"])
def register_user():
    body = request.json
    name = body.get("name")
    email = body.get("email")
    password = body.get("password")
    user = users.find_one({"email": email})
    if user:
        return {"Message": "User already exists"}, 409
    user = {
        "Author ID": str(uuid4()),
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "role": "user"
    }
    users.insert_one(user)
    return {
        "Message": "User Registered"
    }, 201

@app.route("/login", methods=["POST"])
def login_user():
    body = request.json
    email = body.get("email")
    password = body.get("password")
    user = users.find_one({"email": email})
    if not user:
        return {"Message": "User does not exist"}, 404
    token = create_access_token(identity=user["Author ID"])
    return {
        "Message": "Login Successful",
        "email": user["email"],
        "Access token": token
    }, 200

@app.route("/blogs", methods=["GET"])
@jwt_required()
def get_current_user_blogs():
    author_id = get_jwt_identity()
    blog_list = []
    result = blogs.find({"Author ID": author_id})
    for blog in result:
        blog["_id"] = str(blog["_id"])
        blog_list.append(blog)
    return blog_list, 200

if __name__ == "__main__":
    app.run(debug=True)