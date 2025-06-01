import jwt
from functools import wraps
from flask import request, jsonify
import re

from app.app import env_var
from app.models.users import Users

fieldTypeFormattedName = {
    'str': 'STRING',
    'int': 'INTEGER'
}

pathsToSanitize = {
    "^/api/task/update/\d+$": "/api/task/update",
    "^/api/task/assign/\d+$": "/api/task/assign",
    "^/api/task/comment/\d+$": "/api/task/comment"
}

requiredFields = {
    '/register': [ 'name', 'email', 'password' ] ,
    '/api/task/create': [ 'title', 'description', 'type' ],
    '/api/task/assign': [ 'assigned_to' ],
    '/api/task/comment': [ 'text' ]
}

fieldByType = {
    '/register': { 'name': 'str', 'email': 'str', 'password': 'str' },
    '/api/task/create': { 'title': 'str', 'description': 'str', 'type': 'str' },
    '/api/task/update': { 'title': 'str', 'description': 'str', 'type': 'str', 'status': 'str' },
    '/api/task/assign': { 'assigned_to': 'int' },
    '/api/task/comment': { 'text': 'str' }
}

fieldNotEmpty = {
    '/register': [ 'name', 'email', 'password' ],
    '/api/task/create': [ 'title', 'description', 'type' ],
    '/api/task/update': [ 'title', 'description', 'type', 'status' ],
    '/api/task/assign': [ 'assigned_to' ],
    '/api/task/comment': [ 'text' ]
}

fieldIsIn = {
    '/api/task/create': { 'type': [ 'feature', 'bugfix', 'hotfix' ] },
    '/api/task/update': { 'type': [ 'feature', 'bugfix', 'hotfix' ], 'status': [ 'closed', 'open', 'in_dev', 'blocked', 'in_qa' ] },
}

def validator(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        path = request.path
        requestBody = request.get_json()

        for pathToSanitize in pathsToSanitize.keys():
            if re.search(pathToSanitize, path):
                path = pathsToSanitize[pathToSanitize]

        messages = []
        if path in requiredFields.keys():
            for field in requiredFields[path]:
                if field not in requestBody:
                    messages.append('MISSING_' + field.upper())

        if path in fieldByType.keys():
            for field in requestBody:
                if field in fieldByType[path]:
                    requestFieldType = type(requestBody[field]).__name__ #isinstance(item, str)
                    expectedFieldType = fieldByType[path][field]
                    if requestFieldType != expectedFieldType:
                        messages.append(field.upper() + "_NOT_" + fieldTypeFormattedName[expectedFieldType])

        if path in fieldNotEmpty.keys():
            for field in requestBody:
                if field in fieldNotEmpty[path] and type(requestBody[field]).__name__ == 'str':
                    if len(requestBody[field]) == 0:
                        messages.append('EMPTY_' + field.upper())
        
        if path in fieldIsIn.keys():
            for field in requestBody:
                if field in fieldIsIn[path] and requestBody[field] not in fieldIsIn[path][field]:
                    fieldName = 'INVALID_' + field.upper()
                    messages.append(fieldName)
        
        if messages:
            return jsonify({'message': messages, 'success': False}), 400

        return f(*args, **kwargs)
    return decorated


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': [ "MISSING_TOKEN" ], 'success': False}), 401

        token = token.split()[1]
        try:
            data = jwt.decode(token, env_var['SECRET'], algorithms=['HS256'])
            current_user = Users.query.filter(Users.email == data['email']).one()
        except:
            return jsonify({'message': [ "INVALID_TOKEN" ], 'success': False}), 401

        return f(current_user, *args, **kwargs)
    return decorated
