import jwt
import datetime
import re
from flask import make_response, request, jsonify
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

from app.app import app, database, env_var
from app.models.users import Users, user_schema, users_schema
from app.routes import validations

@app.post("/register")
@validations.validator
def register():
    user = Users.query.filter_by(email = request.json['email']).first()
    if user:
        return make_response(jsonify({ "message": [ "EMAIL_ALREADY_TAKEN" ], "success": False }), 400)
    
    if not re.search("^(.+)@(\\S+)$", request.json['email']):
        return make_response(jsonify({ "message": [ "INVALID_EMAIL" ], "success": False }), 400)

    password = generate_password_hash(request.json['password'])

    user = Users(request.json['name'], request.json['email'], password)
    database.session.add(user)
    database.session.commit()

    result = user_schema.dump(user)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.post("/login")
@validations.validator
def login():
    user = Users.query.filter(Users.email == request.json['username']).first()
    if not user:
        return make_response(jsonify({ "message": [ "USER_NOT_FOUND" ], "success": False }), 400)

    if not check_password_hash(user.password, request.json['password']):
        return make_response(jsonify({ "message": [ "INVALID_CREDENTIALS" ], "success": False }), 400)

    token = jwt.encode({'email': user.email, 'exp': datetime.datetime.now() + datetime.timedelta(hours=12) }, env_var['SECRET'])
    return make_response(jsonify({ "token": token, "success": True }), 200)

@app.get("/api/users/list")
def listUsers():
    users = Users.query.order_by(Users.id.desc()).all()

    result = {}
    result['users'] = users_schema.dump(users)
    result['total'] = len(users)

    return make_response(jsonify({ "data": result, "success": True }), 200)
