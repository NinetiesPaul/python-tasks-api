import datetime
from flask import make_response, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, mysql
from routes import validations
from models.taskHistory import TaskHistory
from models.tasks import Tasks, task_schema, tasks_schema
from models.users import Users, user_schema, users_schema

@app.post("/api/task/create")
@validations.token_required
def post_task(current_user):
    data = request.get_json()

    if 'title' not in data:
        return make_response(jsonify({ "msg": "missing required parameter: title", "success": False }), 400)

    if 'description' not in data:
        return make_response(jsonify({ "msg": "missing required parameter: description", "success": False }), 400)

    if 'type' not in data:
        return make_response(jsonify({ "msg": "missing required parameter: type", "success": False }), 400)
    
    elif data['type'] not in Tasks.allowedTypes():
        return make_response(jsonify({ "msg": "Invalid task type: must be one of 'feature' 'bugfix' 'hotfix'", "success": False }), 400)

    task = Tasks(data['title'], data['description'], data['type'], current_user)
    mysql.session.add(task)
    mysql.session.commit()

    result = task_schema.dump(task)
    del result['history']
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.get("/api/task/list")
@validations.token_required
def get_tasks(current_user):
    args = request.args

    if not args:
        tasks = Tasks.query.order_by(Tasks.id.desc()).all()

    else:
        tasks = Tasks.query

        if 'type' in args:
            if args['type'] not in Tasks.allowedTypes():
                return make_response(jsonify({ "msg": "Invalid task type: must be one of 'feature' 'bugfix' 'hotfix'", "success": False }), 400)
            tasks = tasks.filter(Tasks.type == args['type'])

        if 'status' in args:
            if args['status'] not in Tasks.allowedStatuses():
                return make_response(jsonify({ "msg": "Invalid task status: must be one of 'open' 'closed' 'in_dev' 'blocked' 'in_qa'", "success": False }), 400)
            tasks = tasks.filter(Tasks.status == args['status'])

        if 'created_by' in args:
            user = Users.query.get(args['created_by'])
            if not user:
                return make_response(jsonify({ "msg": "USER_NOT_FOUND", "success": False }), 404)
            tasks = tasks.filter(Tasks.created_by_id == args['created_by'])

        tasks = tasks.order_by(Tasks.id.desc()).all()

    result = {}
    result['tasks'] = tasks_schema.dump(tasks)
    result['total'] = len(tasks)

    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.get("/api/task/view/<id>")
@validations.token_required
def get_task(current_user, id):
    task = Tasks.query.get(id)

    if not task:
        return make_response(jsonify({ "msg": "TASK_NOT_FOUND", "success": False }), 404)

    result = task_schema.dump(task)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.put("/api/task/update/<id>")
@validations.token_required
def put_task(current_user, id):
    data = request.get_json()

    task = Tasks.query.get(id)

    if not task:
        return make_response(jsonify({ "msg": "TASK_NOT_FOUND", "success": False }), 404)

    if task.status == 'closed':
        return make_response(jsonify({ "msg": "Invalid operation: cannot update a closed task", "success": False }), 404)
    
    if 'status' in data and data['status'] == 'closed':
        return make_response(jsonify({ "msg": "Invalid operation: use PUT /api/task/close/{id} to close a task", "success": False }), 400)
    
    historyEntries = {}

    if 'title' in data and task.title != data['title']:
        historyEntries['title'] = [ task.title, data['title'] ]
        task.title = data['title']
    
    if 'description' in data and task.description != data['description']:
        historyEntries['description'] = [ task.description, data['description'] ]
        task.description = data['description']

    if 'type' in data and task.type != data['type']:
        if data['type'] not in Tasks.allowedTypes():
            return make_response(jsonify({ "msg": "Invalid task type: must be one of 'feature' 'bugfix' 'hotfix'", "success": False }), 400)
        
        historyEntries['type'] = [ task.type, data['type'] ]
        task.type = data['type']

    if 'status' in data and task.status != data['status']:
        if data['status'] not in Tasks.allowedStatuses():
            return make_response(jsonify({ "msg": "Invalid task status: must be one of 'open' 'closed' 'in_dev' 'blocked' 'in_qa'", "success": False }), 400)
        historyEntries['status'] = [ task.status, data['status'] ]
        task.status = data['status']

    mysql.session.commit()

    for entry in historyEntries:
        taskHistory = TaskHistory(entry, historyEntries[entry][0], historyEntries[entry][1], current_user, task)
        mysql.session.add(taskHistory)
        mysql.session.commit()

    result = task_schema.dump(task)
    del result['history']
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.put("/api/task/close/<id>")
@validations.token_required
def close_task(current_user, id):
    task = Tasks.query.get(id)

    if not task:
        return make_response(jsonify({ "msg": "TASK_NOT_FOUND", "success": False }), 404)
    
    if task.status == 'closed':
        return make_response(jsonify({ "msg": "Invalid operation: cannot close a closed task", "success": False }), 404)
    
    taskHistory = TaskHistory('status', task.status, 'closed', current_user, task)
    mysql.session.add(taskHistory)
    mysql.session.commit()

    task.status = 'closed'
    task.closed_on = datetime.datetime.now()
    task.closed_by = current_user

    mysql.session.commit()
    result = task_schema.dump(task)
    del result['history']
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.delete("/api/task/delete/<id>")
@validations.token_required
def delete_task(current_user, id):
    task = Tasks.query.get(id)

    if not task:
        return make_response(jsonify({ "msg": "TASK_NOT_FOUND", "success": False }), 404)
    
    mysql.session.delete(task)
    mysql.session.commit()
    return make_response(jsonify({ "msg": "Task id '" + id + "' was deleted", "success": True }), 200)
