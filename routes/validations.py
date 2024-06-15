import jwt
from functools import wraps
from flask import request, jsonify

from app import env_var
from models.users import Users

fieldsByRequest = {
    '/login': [ 'username', 'password' ],
    '/register': [ 'name', 'email', 'password' ] 
}

def validator(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        path = request.path
        requestBody = request.get_json()

        messages = []
        for field in fieldsByRequest[path]:
            if field not in requestBody:
                messages.append('INVALID_REQUEST_MISSING_' + field.upper())
        
        if messages:
            return jsonify({'msg': messages, 'success': False}), 400

        return f(*args, **kwargs)
    return decorated


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
