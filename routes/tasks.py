import datetime
from flask import make_response, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, mysql

from routes import users

from models.tasks import Tasks, task_schema, tasks_schema

@app.post("/task")
@users.token_required
def post_task(current_user):
    data = request.get_json()

    if 'title' not in data:
        return make_response(jsonify({ "msg": "missing required parameter: title", "success": False }), 400)

    if 'description' not in data:
        return make_response(jsonify({ "msg": "missing required parameter: description", "success": False }), 400)

    if 'type' not in data:
        return make_response(jsonify({ "msg": "missing required parameter: type", "success": False }), 400)
    
    elif data['type'] not in Tasks.allowedTypes():
        return make_response(jsonify({ "msg": "Invalid type given", "success": False }), 400)

    task = Tasks(data['title'], data['description'], current_user.id, data['type'])
    mysql.session.add(task)
    mysql.session.commit()

    result = task_schema.dump(task)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.get("/tasks")
@users.token_required
def get_tasks(current_user):
    args = request.args

    if not args:
        tasks = Tasks.query.all()

    else:
        tasks = Tasks.query

        if 'type' in args:
            if args['type'] not in Tasks.allowedTypes():
                return make_response(jsonify({ "msg": "Invalid type given", "success": False }), 400)
            tasks = tasks.filter(Tasks.type == args['type'])

        if 'status' in args:
            if args['status'] not in Tasks.allowedStatuses():
                return make_response(jsonify({ "msg": "Invalid status given", "success": False }), 400)
            tasks = tasks.filter(Tasks.status == args['status'])

        tasks = tasks.all()

    result = tasks_schema.dump(tasks)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.put("/task/<id>")
@users.token_required
def put_task(current_user, id):
    data = request.get_json()

    task = Tasks.query.get(id)

    if not task:
        return make_response(jsonify({ "msg": "No task found with given id", "success": False }), 404)
    
    if 'title' in data:
        task.title = data['title']
    
    if 'description' in data:
        task.description = data['description']

    if 'type' in data:
        if data['type'] not in Tasks.allowedTypes():
            return make_response(jsonify({ "msg": "Invalid type given", "success": False }), 400)
        task.type = data['type']

    if 'status' in data:
        if data['status'] not in Tasks.allowedStatuses():
            return make_response(jsonify({ "msg": "Invalid status given", "success": False }), 400)
        if data['status'] == 'closed':
            return make_response(jsonify({ "msg": "please use the appropriate URL: PUT /task/{id}/closed", "success": False }), 400)
        task.status = data['status']

    mysql.session.commit()
    result = task_schema.dump(task)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.put("/task/<id>/close")
@users.token_required
def close_task(current_user, id):
    task = Tasks.query.get(id)

    if not task:
        return make_response(jsonify({ "msg": "No task found with given id", "success": False }), 404)
    
    if task.status != 'closed':
        task.status = 'closed'
        task.closed_on = datetime.datetime.now()

    mysql.session.commit()
    result = task_schema.dump(task)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.delete("/task/<id>")
@users.token_required
def delete_task(current_user, id):
    task = Tasks.query.get(id)

    if not task:
        return make_response(jsonify({ "msg": "No task found with given id", "success": False }), 404)
    
    mysql.session.delete(task)
    mysql.session.commit()
    result = task_schema.dump(task)
    return make_response(jsonify({ "msg": "Task deleted", "success": True }), 200)
