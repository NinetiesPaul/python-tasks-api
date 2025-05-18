import json
import datetime
from app import database, ma
from models.users import user_schema
from models.taskHistory import taskHistory_schema
from models.taskComment import taskComment_schema
from models.taskAssignee import taskAssignees_schema
from marshmallow import fields

class Tasks(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    title = database.Column(database.String(55), nullable=False)
    description = database.Column(database.String(255), nullable=False)
    type = database.Column(database.String(255), nullable=False)
    status = database.Column(database.String(255), nullable=False)
    created_on = database.Column(database.DateTime, nullable=False)
    created_by_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    closed_on = database.Column(database.DateTime, nullable=True)
    closed_by_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=True)

    comments = database.relationship('TaskComment', backref='task', lazy='select', foreign_keys="TaskComment.task_id")
    history = database.relationship('TaskHistory', backref='task', lazy='select', foreign_keys="TaskHistory.task_id")
    assignees = database.relationship('TaskAssignees', backref='task', lazy='select', foreign_keys="TaskAssignees.task_id")

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
    assignees = fields.Nested(taskAssignees_schema, many=True)
    class Meta:
        fields = ('id', 'title', 'description', 'type', 'status', 'created_on', 'created_by', 'closed_on', 'closed_by', 'assignees')

class TaskSchema(ma.Schema):
    created_by = fields.Nested(user_schema, only=["id", "email", "name"])
    closed_by = fields.Nested(user_schema, only=["id", "email", "name"])
    comments = fields.Nested(taskComment_schema, many=True)
    history = fields.Nested(taskHistory_schema, many=True)
    assignees = fields.Nested(taskAssignees_schema, many=True)
    class Meta:
        fields = ('id', 'title', 'description', 'type', 'status', 'created_on', 'created_by', 'closed_on', 'closed_by', 'comments', 'history', 'assignees')

task_schema = TaskSchema()
tasks_schema = TasksSchema(many=True)
