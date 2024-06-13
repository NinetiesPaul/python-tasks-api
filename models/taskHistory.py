import json
import datetime
from app import mysql, ma
from models.users import user_schema
from marshmallow import fields

class TaskHistory(mysql.Model):
    id = mysql.Column(mysql.Integer, primary_key=True, auto_increment=True)
    field = mysql.Column(mysql.String(55), nullable=False)
    changed_from = mysql.Column(mysql.String(255), nullable=False)
    changed_to = mysql.Column(mysql.String(255), nullable=False)
    changed_on = mysql.Column(mysql.DateTime, nullable=True)
    changed_by_id = mysql.Column(mysql.Integer, mysql.ForeignKey('users.id'), nullable=False)
    task_id = mysql.Column(mysql.Integer, mysql.ForeignKey('tasks.id'), nullable=True)

    def __init__(self, field, changed_from, changed_to, changed_by, task, changed_on = datetime.datetime.now()):
        self.field = field
        self.changed_from = changed_from
        self.changed_to = changed_to
        self.changed_by = changed_by
        self.task = task
        self.changed_on = changed_on

class TaskHistorySchema(ma.Schema):
    changed_by = fields.Nested(user_schema, only=["id", "email", "name"])
    class Meta:
        fields = ('id', 'field', 'changed_from', 'changed_to', 'changed_on', 'changed_by')

taskHistory_schema = TaskHistorySchema()
taskHistories_schema = TaskHistorySchema(many=True)
