from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import dotenv_values
from flask_cors import CORS

env_var = dotenv_values(".env")

if env_var['ENVIRONMENT'] == 'testing':
    connection_uri = env_var['DB_URL_TESTING']
else:
    connection_uri = env_var['DB_URL']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = connection_uri
CORS(app)
mysql = SQLAlchemy(app)
ma = Marshmallow(app)

from routes.users import *

from routes.tasks import *
