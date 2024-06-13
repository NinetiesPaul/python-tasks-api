import json
import datetime
from app import mysql, ma
from models.users import user_schema
from models.taskHistory import taskHistory_schema
from marshmallow import fields

class Tasks(mysql.Model):
    id = mysql.Column(mysql.Integer, primary_key=True, auto_increment=True)
    title = mysql.Column(mysql.String(55), nullable=False)
    description = mysql.Column(mysql.String(255), nullable=False)
    type = mysql.Column(mysql.String(255), nullable=False)
    status = mysql.Column(mysql.String(255), nullable=False)
    created_on = mysql.Column(mysql.DateTime, nullable=False)
    created_by_id = mysql.Column(mysql.Integer, mysql.ForeignKey('users.id'), nullable=False)
    closed_on = mysql.Column(mysql.DateTime, nullable=True)
    closed_by_id = mysql.Column(mysql.Integer, mysql.ForeignKey('users.id'), nullable=True)

    task_history = mysql.relationship('TaskHistory', backref='task', lazy='joined', foreign_keys="TaskHistory.task_id")

    def __init__(self, title, description, type, created_by, created_on = datetime.datetime.now(), closed_on = None, closed_by = None, status = "open"):
        self.title = title
        self.description = description
        self.type = type
        self.status = status
        self.created_on = created_on
        self.created_by = created_by
        self.closed_on = closed_on
        self.closed_by = closed_by
    
    def allowedTypes():
        return [ 'feature', 'bugfix', 'hotfix' ]
    
    def allowedStatuses():
        return [ 'open', 'closed', 'in_dev', 'blocked', 'in_qa' ]

class TasksSchema(ma.Schema):
    created_by = fields.Nested(user_schema, only=["id", "email", "name"])
    closed_by = fields.Nested(user_schema, only=["id", "email", "name"])
    class Meta:
        fields = ('id', 'title', 'description', 'type', 'status', 'created_on', 'created_by', 'closed_on', 'closed_by')

class TaskSchema(ma.Schema):
    created_by = fields.Nested(user_schema, only=["id", "email", "name"])
    closed_by = fields.Nested(user_schema, only=["id", "email", "name"])
    task_history = fields.Nested(taskHistory_schema, many=True)
    class Meta:
        fields = ('id', 'title', 'description', 'type', 'status', 'created_on', 'created_by', 'closed_on', 'closed_by', 'task_history')

task_schema = TaskSchema()
tasks_schema = TasksSchema(many=True)
