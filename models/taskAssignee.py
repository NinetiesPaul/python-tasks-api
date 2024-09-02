import json
import datetime
from app import mysql, ma
from models.users import user_schema
from marshmallow import fields

class TaskAssignees(mysql.Model):
    __table_args__ = (
        mysql.UniqueConstraint('assigned_to_id', 'task_id'),
    )
    id = mysql.Column(mysql.Integer, primary_key=True, auto_increment=True)
    assigned_by_id = mysql.Column(mysql.Integer, mysql.ForeignKey('users.id'), nullable=False)
    assigned_to_id = mysql.Column(mysql.Integer, mysql.ForeignKey('users.id'), nullable=False)
    task_id = mysql.Column(mysql.Integer, mysql.ForeignKey('tasks.id'), nullable=True)

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
