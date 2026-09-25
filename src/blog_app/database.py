from pymongo import MongoClient
client = MongoClient('mongodb+srv://guffranjgshaik_db_user:zFMHm7NoVSVvHUky@studentattendance.u8cdbrl.mongodb.net/?appName=StudentAttendance')
db = client["blog_app"]
users = db["users"]
blogs = db["blogs"]
comments = db["comments"]