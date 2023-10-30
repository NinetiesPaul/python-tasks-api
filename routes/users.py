import jwt
import datetime
import re
from flask import make_response, request, jsonify
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, mysql, env_var

from models.users import Users, user_schema

@app.post("/register")
def register():
    user = Users.query.filter_by(email = request.json['email']).first()
    if user:
        return make_response(jsonify({ "msg": "E-mail already taken", "success": False }), 404)
    
    if not re.search("^(.+)@(\\S+)$", request.json['email']):
        return make_response(jsonify({ "msg": "E-mail is invalid", "success": False }), 404)


    password = generate_password_hash(request.json['password'])

    user = Users(request.json['name'], request.json['email'], password)
    mysql.session.add(user)
    mysql.session.commit()

    result = user_schema.dump(user)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.post("/login")
def login():
    try: 
        user = Users.query.filter(Users.email == request.json['username']).one()
    except:
        return make_response(jsonify({ "msg": "user not found", "success": False }), 404)

    if check_password_hash(user.password, request.json['password']):
        token = jwt.encode({'email': user.email, 'exp': datetime.datetime.now() + datetime.timedelta(hours=12) }, env_var['SECRET'])
        return make_response(jsonify({ "token": token, "success": True }), 200)

    return make_response(jsonify({ "msg": "invalid credentials", "success": False }), 400)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'msg': 'token is missing', 'success': False}), 401

        token = token.split()[1]
        try:
            data = jwt.decode(token, env_var['SECRET'], algorithms=['HS256'])
            current_user = Users.query.filter(Users.email == data['email']).one()
        except:
            return jsonify({'msg': 'token is invalid or expired', 'success': False}), 401

        return f(current_user, *args, **kwargs)
    return decorated
