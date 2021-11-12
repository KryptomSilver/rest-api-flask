from flask import Flask, request, Response
from flask.json import jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId

app = Flask(__name__)

# DB

app.config["MONGO_URI"] = "mongodb://localhost:27017/pythoncrud"

mongo = PyMongo(app)

# Crete user


@app.route("/users", methods=["POST"])
def create_user():
    user = request.json["user"]
    password = request.json["password"]
    email = request.json["email"]
    if user and password and email:
        hashed_password = generate_password_hash(password)
        id = mongo.db.users.insert_one({
            "user": user,
            "password": hashed_password,
            "email": email
        })
        response = {
            "id": str(id.inserted_id),
            "msg": "ok"
        }
        return response
    else:
        return bad_request()

# Get users


@app.route("/users", methods=["GET"])
def get_users():
    users = mongo.db.users.find()
    data = json_util.dumps(users)
    return Response(data, mimetype="application/json")

# Get user


@app.route("/users/<id>", methods=["GET"])
def get_user(id):
    user = mongo.db.users.find_one({"_id": ObjectId(id)})
    if(user):
        response = json_util.dumps(user)
        return Response(response, mimetype="application/json")
    else:
        response = jsonify({
            "msg": "Not found user"
        })
        response.status_code = 404
        return response

# Delete user


@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    user = mongo.db.users.find_one({"_id": ObjectId(id)})
    if(user):
        mongo.db.users.find_one_and_delete({"_id": ObjectId(id)})
        response = jsonify({
            "msg": "User " + id + " deleted"
        })
        return response
    else:
        response = jsonify({
            "msg": "Not found user"
        })
        response.status_code = 404
        return response

# Update user


@app.route("/users/<id>", methods=["PUT"])
def update_user(id):
    user = request.json["user"]
    email = request.json["email"]
    password = request.json["password"]
    if email and password and user:
        user = mongo.db.users.find_one({"_id": ObjectId(id)})
        if(user):
            hashed_password = generate_password_hash(password)
            mongo.db.users.update_one({"_id": ObjectId(id)}, {"$set": {
                "user": user,
                "email": email,
                "password": hashed_password
            }

            })
            return {"msg": "Update user"}
        else:
            response = jsonify({
                "msg": "Not found user"
            })
            response.status_code = 404
            return response
    else:
        return bad_request()

# Handler 404


@app.errorhandler(404)
def not_found(error=None):
    msg = jsonify({
        "msg": "Recurse not found: " + request.url,
        "status": 404
    })
    msg.status_code = 404
    return msg

# Handler 400


@app.errorhandler(400)
def bad_request(error=None):
    msg = jsonify({
        "msg": "Missing fields",
        "status": 400
    })
    msg.status_code = 400
    return msg


if __name__ == "__main__":
    app.run(debug=True)
