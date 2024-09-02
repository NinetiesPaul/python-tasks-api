import datetime
from flask import make_response, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, mysql
from routes import validations
from models.taskHistory import TaskHistory
from models.taskAssignee import TaskAssignees, taskAssignee_schema
from models.tasks import Tasks, task_schema, tasks_schema
from models.users import Users, user_schema, users_schema

@app.post("/api/task/create")
@validations.token_required
@validations.validator
def post_task(current_user):
    data = request.get_json()

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
        errorMessages = []

        if 'type' in args:
            if args['type'] not in Tasks.allowedTypes():
                errorMessages.append("INVALID_TYPE")
            tasks = tasks.filter(Tasks.type == args['type'])

        if 'status' in args:
            if args['status'] not in Tasks.allowedStatuses():
                errorMessages.append("INVALID_STATUS")
            tasks = tasks.filter(Tasks.status == args['status'])

        if 'created_by' in args:
            user = Users.query.get(args['created_by'])
            if not user:
                errorMessages.append("USER_NOT_FOUND")
            else:
                tasks = tasks.filter(Tasks.created_by_id == args['created_by'])

        if len(errorMessages) > 0:
            return make_response(jsonify({ "message": errorMessages, "success": False }), 400)

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
        return make_response(jsonify({ "message": [ "TASK_NOT_FOUND" ], "success": False }), 404)

    result = task_schema.dump(task)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.put("/api/task/update/<id>")
@validations.token_required
@validations.validator
def put_task(current_user, id):
    data = request.get_json()

    task = Tasks.query.get(id)
    if not task:
        return make_response(jsonify({ "message": [ "TASK_NOT_FOUND" ], "success": False }), 404)

    if task.status == 'closed':
        return make_response(jsonify({ "message": [ "TASK_CLOSED" ], "success": False }), 404)
    
    if 'status' in data and data['status'] == 'closed':
        return make_response(jsonify({ "message": [ "CAN_NOT_UPDATE_TO_CLOSE" ], "success": False }), 400)
    
    historyEntries = {}

    if 'title' in data and task.title != data['title']:
        historyEntries['title'] = [ task.title, data['title'] ]
        task.title = data['title']
    
    if 'description' in data and task.description != data['description']:
        historyEntries['description'] = [ task.description, data['description'] ]
        task.description = data['description']

    if 'type' in data and task.type != data['type']:
        historyEntries['type'] = [ task.type, data['type'] ]
        task.type = data['type']

    if 'status' in data and task.status != data['status']:
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
        return make_response(jsonify({ "message": [ "TASK_NOT_FOUND" ], "success": False }), 404)
    
    if task.status == 'closed':
        return make_response(jsonify({ "message": [ "TASK_ALREADY_CLOSED" ], "success": False }), 404)
    
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

@app.post("/api/task/assign/<taskId>")
@validations.token_required
def assign_task(current_user, taskId):
    requestData = request.get_json()
    task = Tasks.query.get(taskId)

    if not task:
        return make_response(jsonify({ "message": [ "TASK_NOT_FOUND" ], "success": False }), 404)
    
    assignedTo = Users.query.get(requestData['assigned_to'])
    if not assignedTo:
        return make_response(jsonify({ "message": [ "USER_NOT_FOUND" ], "success": False }), 404)

    try:
        taskAssignee = TaskAssignees(current_user, assignedTo, task)
        mysql.session.add(taskAssignee)
        mysql.session.commit()
    except Exception as e:
        if type(e) == mysql.exc.IntegrityError:
            return make_response(jsonify({ "message": [ "USER_ALREADY_ASSIGNED" ], "success": False }), 202)
    
    taskHistory = TaskHistory("added_assignee", "", assignedTo.name, current_user, task)
    mysql.session.add(taskHistory)
    mysql.session.commit()

    mysql.session.commit()
    result = taskAssignee_schema.dump(taskAssignee)
    return make_response(jsonify({ "data": result, "success": True }), 200)

@app.delete("/api/task/unassign/<assignmentId>")
@validations.token_required
def unassign_task(current_user, assignmentId):
    assignment = TaskAssignees.query.get(assignmentId)

    if not assignment:
        return make_response(jsonify({ "message": [ "ASSIGNMENT_NOT_FOUND" ], "success": False }), 404)
    
    mysql.session.delete(assignment)
    mysql.session.commit()

    assignedTo = Users.query.get(assignment.assigned_to_id)
    task = Tasks.query.get(assignment.task_id)

    taskHistory = TaskHistory("removed_assignee", "", assignedTo.name, current_user, task)
    mysql.session.add(taskHistory)
    mysql.session.commit()

    return make_response(jsonify({ "data": None, "success": True }), 200)

@app.delete("/api/task/delete/<id>")
@validations.token_required
def delete_task(current_user, id):
    task = Tasks.query.get(id)

    if not task:
        return make_response(jsonify({ "msg": "TASK_NOT_FOUND", "success": False }), 404)
    
    mysql.session.delete(task)
    mysql.session.commit()
    return make_response(jsonify({ "msg": "Task id '" + id + "' was deleted", "success": True }), 200)
