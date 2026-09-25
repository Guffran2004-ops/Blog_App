from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .database import blogs, comments
from datetime import datetime
from bson import ObjectId
blogs_bp = Blueprint("blogs",__name__,url_prefix="/api")

@blogs_bp.route("/blogs", methods=["POST"])
@jwt_required()
def create_blog():
    body = request.json
    title = body.get("title")
    content = body.get("content")
    tags = body.get("tags", [])
    author_id = get_jwt_identity()
    blog = {
        "title": title,
        "content": content,
        "Author ID": author_id,
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "published_at": None,
        "tags": tags,
        "likes": []
    }
    result = blogs.insert_one(blog)
    return {
        "Message": "Blog created successfully",
        "Blog ID": str(result.inserted_id)
    }, 201

@blogs_bp.route("/blogs/<blog_id>", methods=["PUT"])
@jwt_required()
def edit_blog(blog_id):
    author_id = get_jwt_identity()
    blog_id = ObjectId(blog_id)
    blog = blogs.find_one({"_id": blog_id})
    if blog["Author ID"] != author_id:
      return {"Message": "You cannot edit this blog"}, 403
    if not blog:
        return {
            "Message": "Blog not found"
        }, 404
    body = request.json
    title = body.get("title")
    content = body.get("content")
    tags = body.get("tags")
    update = {}
    if title:
        update["title"] = title
    if content:
        update["content"] = content
    if tags is not None:
        update["tags"] = tags
    update["updated_at"] = datetime.utcnow()
    blogs.update_one({"_id": blog_id},{"$set": update})
    return {
        "Message": "Blog updated successfully"
    }, 200

@blogs_bp.route("/blogs/<blog_id>/publish", methods=["PATCH"])
@jwt_required()
def publish_blog(blog_id):
    author_id = get_jwt_identity()
    blog_id = ObjectId(blog_id)
    blog = blogs.find_one({"_id": blog_id})
    if blog["Author ID"] != author_id:
     return {"Message": "You cannot edit this blog"}, 403
    if not blog:
        return {
            "Message": "Blog not found"
        }, 404
    blogs.update_one(
        {"_id": blog_id},
        {
            "$set": {
                "status": "published",
                "published_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    return {
        "Message": "Blog published successfully"
    }, 200

@blogs_bp.route("/blogs/<blog_id>", methods=["GET"])
def get_blog(blog_id):
    blog_id = ObjectId(blog_id)
    blog = blogs.find_one({"_id": blog_id})
    if not blog:
        return {
            "Message": "Blog not found"
        }, 404
    blog["_id"] = str(blog["_id"])
    return blog, 200

@blogs_bp.route("/blogs", methods=["GET"])
def get_all_blogs():
    page = request.args.get("page",1,type=int)
    limit = request.args.get("limit",10,type=int)
    if page < 1 or limit < 1:
        return {
            "Message": "Invalid page or limit"
        }, 400
    query = {
        "status": "published"
    }
    search = request.args.get("q")
    if search:
        query["$or"] = [
            {
                "title": {
                    "$regex": search,
                    "$options": "i"
                }
            },
            {
                "content": {
                    "$regex": search,
                    "$options": "i"
                }
            }
        ]
    tag = request.args.get("tag")
    if tag:
        query["tags"] = tag
    total = blogs.count_documents(query)
    skip = (page - 1) * limit
    result = blogs.find(query) \
        .sort("published_at", -1) \
        .skip(skip) \
        .limit(limit)

    blog_list = []
    for blog in result:
        blog["_id"] = str(blog["_id"])
        blog_list.append(blog)
    return {
        "blogs": blog_list,
        "page": page,
        "limit": limit,
        "total": total
    }, 200

@blogs_bp.route("/blogs/<blog_id>", methods=["DELETE"])
@jwt_required()
def delete_blog(blog_id):
    author_id = get_jwt_identity()
    blog_id = ObjectId(blog_id)
    blog = blogs.find_one({"_id": blog_id})
    if blog["Author ID"] != author_id:
     return {"Message": "You cannot edit this blog"}, 403
    if not blog:
        return {
            "Message": "Blog not found"
        }, 404
    blogs.delete_one({
        "_id": blog_id
    })
    return {
        "Message": "Blog deleted successfully"
    }, 200

@blogs_bp.route("/blogs/<blog_id>/like", methods=["POST"])
@jwt_required()
def like_blog(blog_id):
    author_id = get_jwt_identity()
    blog_id = ObjectId(blog_id)
    blog = blogs.find_one({"_id": blog_id,"status": "published"})
    if not blog:
        return {
            "Message": "Published blog not found"
        }, 404
    blogs.update_one(
        {"_id": blog_id},
        {
            "$addToSet": {
                "likes": author_id
            }
        }
    )
    return {
        "Message": "liked"
    }, 200

@blogs_bp.route("/blogs/<blog_id>/like", methods=["DELETE"])
@jwt_required()
def unlike_blog(blog_id):
    author_id = get_jwt_identity()
    blog_id = ObjectId(blog_id)
    blog = blogs.find_one({"_id": blog_id,"status": "published"})
    if not blog:
        return {
            "Message": "Blog not found"
        }, 404
    blogs.update_one(
        {"_id": blog_id},
        {
            "$pull": {
                "likes": author_id
            }
        }
    )
    return {
        "Message": "unliked"
    }, 200

@blogs_bp.route("/blogs/<blog_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(blog_id):
    author_id = get_jwt_identity()
    blog_id = ObjectId(blog_id)
    blog = blogs.find_one({"_id": blog_id,"status": "published"})
    if not blog:
        return {
            "Message": "Blog not found"
        }, 404
    body = request.json
    comment_text = body.get("comment")
    comment = {
        "Blog ID": blog_id,
        "Author ID": author_id,
        "comment": comment_text,
        "created_at": datetime.utcnow()
    }
    result = comments.insert_one(comment)
    return {
        "Message": "Comment added successfully",
        "Comment ID": str(result.inserted_id)
    }, 201

@blogs_bp.route("/blogs/<blog_id>/comments", methods=["GET"])
def get_comments(blog_id):
    blog_id = ObjectId(blog_id)
    blog = blogs.find_one({"_id": blog_id,"status": "published"})
    if not blog:
        return {
            "Message": "Blog not found"
        }, 404
    result = comments.find({"Blog ID": blog_id})
    comment_list = []
    for comment in result:
        comment["_id"] = str(comment["_id"])
        comment["Blog ID"] = str(comment["Blog ID"])
        comment_list.append(comment)
    return comment_list, 200