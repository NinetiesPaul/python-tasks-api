from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import dotenv_values

env_var = dotenv_values(".env")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = env_var['DB_URL']
mysql = SQLAlchemy(app)
ma = Marshmallow(app)

from routes.users import *

from routes.tasks import *
