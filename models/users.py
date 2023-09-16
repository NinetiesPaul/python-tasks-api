import json
from app import mysql, ma

class Users(mysql.Model):
    id = mysql.Column(mysql.Integer, primary_key=True, auto_increment=True)
    username = mysql.Column(mysql.String(255), unique=True, nullable=False)
    password = mysql.Column(mysql.String(255), nullable=False)

    createdBy = mysql.relationship('Tasks', backref='created_by', lazy='joined', foreign_keys="Tasks.created_by_id")
    closedBy = mysql.relationship('Tasks', backref='closed_by', lazy='joined', foreign_keys="Tasks.closed_by_id")

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UsersSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')

user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
