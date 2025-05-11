import json
import datetime
from app import mysql, ma
from models.users import user_schema
from marshmallow import fields

class TaskComment(mysql.Model):
    id = mysql.Column(mysql.Integer, primary_key=True, autoincrement=True)
    comment_text = mysql.Column(mysql.String(255), nullable=False)
    created_on = mysql.Column(mysql.DateTime, nullable=True)
    created_by_id = mysql.Column(mysql.Integer, mysql.ForeignKey('users.id'), nullable=False)
    task_id = mysql.Column(mysql.Integer, mysql.ForeignKey('tasks.id'), nullable=True)

    def __init__(self, text, created_by, task, created_on = datetime.datetime.now()):
        self.comment_text = text
        self.created_on = created_on
        self.created_by = created_by
        self.task = task

class TaskCommentSchema(ma.Schema):
    created_by = fields.Nested(user_schema, only=["id", "email", "name"])

    class Meta:
        fields = ('id', 'comment_text', 'created_on', 'created_by')

taskComment_schema = TaskCommentSchema()
taskComments_schema = TaskCommentSchema(many=True)
