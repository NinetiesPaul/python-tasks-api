import json
import datetime
from app import database, ma
from models.users import user_schema
from marshmallow import fields

class TaskAssignees(database.Model):
    __table_args__ = (
        database.UniqueConstraint('assigned_to_id', 'task_id'),
    )
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    assigned_by_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    assigned_to_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    task_id = database.Column(database.Integer, database.ForeignKey('tasks.id'), nullable=True)

    def __init__(self, assigned_by, assigned_to, task):
        self.assigned_by = assigned_by
        self.assigned_to = assigned_to
        self.task = task

class TaskAssigneesSchema(ma.Schema):
    assigned_by = fields.Nested(user_schema, only=["id", "email", "name"])
    assigned_to = fields.Nested(user_schema, only=["id", "email", "name"])
    class Meta:
        fields = ('id', 'assigned_by', 'assigned_to')

taskAssignee_schema = TaskAssigneesSchema()
taskAssignees_schema = TaskAssigneesSchema(many=True)
