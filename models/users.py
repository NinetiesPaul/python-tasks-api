import json
from app import database, ma

class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String(255), nullable=False)
    email = database.Column(database.String(255), unique=True, nullable=False)
    password = database.Column(database.String(255), nullable=False)

    createdBy = database.relationship('Tasks', backref='created_by', lazy='select', foreign_keys="Tasks.created_by_id")
    closedBy = database.relationship('Tasks', backref='closed_by', lazy='select', foreign_keys="Tasks.closed_by_id")
    changedBy = database.relationship('TaskHistory', backref='changed_by', lazy='select', foreign_keys="TaskHistory.changed_by_id")
    assignedTo = database.relationship('TaskAssignees', backref='assigned_to', lazy='select', foreign_keys="TaskAssignees.assigned_to_id")
    assignedBy = database.relationship('TaskAssignees', backref='assigned_by', lazy='select', foreign_keys="TaskAssignees.assigned_by_id")
    commentCreatedBy = database.relationship('TaskComment', backref='created_by', lazy='select', foreign_keys="TaskComment.created_by_id")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

class UsersSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email')

user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
