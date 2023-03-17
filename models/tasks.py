import json
import datetime
from app import mysql, ma

class Tasks(mysql.Model):
    id = mysql.Column(mysql.Integer, primary_key=True, auto_increment=True)
    title = mysql.Column(mysql.String(55), nullable=False)
    description = mysql.Column(mysql.String(255), nullable=False)
    type = mysql.Column(mysql.String(255), nullable=False)
    status = mysql.Column(mysql.String(255), nullable=False)
    owner = mysql.Column(mysql.Integer, mysql.ForeignKey('users.id'), nullable=False)
    created_on = mysql.Column(mysql.DateTime)
    closed_on = mysql.Column(mysql.DateTime, nullable=True)

    def __init__(self, title, description, owner, type, created_on = datetime.datetime.now(), closed_on = None, status = "open"):
        self.title = title
        self.description = description
        self.type = type
        self.status = status
        self.owner = owner
        self.created_on = created_on
        self.closed_on = closed_on
    
    def allowedTypes():
        return [ 'feature', 'bugfix', 'hotfix' ]
    
    def allowedStatuses():
        return [ 'open', 'closed', 'in_dev', 'blocked', 'in_qa' ]

class TasksSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'type', 'status', 'owner', 'closed_on', 'created_on')

task_schema = TasksSchema()
tasks_schema = TasksSchema(many=True)
