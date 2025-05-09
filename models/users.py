import json
from app import mysql, ma

class Users(mysql.Model):
    id = mysql.Column(mysql.Integer, primary_key=True, auto_increment=True)
    name = mysql.Column(mysql.String(255), nullable=False)
    email = mysql.Column(mysql.String(255), unique=True, nullable=False)
    password = mysql.Column(mysql.String(255), nullable=False)

    createdBy = mysql.relationship('Tasks', backref='created_by', lazy='select', foreign_keys="Tasks.created_by_id")
    closedBy = mysql.relationship('Tasks', backref='closed_by', lazy='select', foreign_keys="Tasks.closed_by_id")
    changedBy = mysql.relationship('TaskHistory', backref='changed_by', lazy='select', foreign_keys="TaskHistory.changed_by_id")
    assignedTo = mysql.relationship('TaskAssignees', backref='assigned_to', lazy='select', foreign_keys="TaskAssignees.assigned_to_id")
    assignedBy = mysql.relationship('TaskAssignees', backref='assigned_by', lazy='select', foreign_keys="TaskAssignees.assigned_by_id")
    commentCreatedBy = mysql.relationship('TaskComment', backref='created_by', lazy='select', foreign_keys="TaskComment.created_by_id")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

class UsersSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email')

user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
