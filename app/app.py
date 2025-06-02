from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import dotenv_values
from flask_cors import CORS
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(base_dir, "..", ".env")

env_var = dotenv_values(env_path)

if env_var['ENVIRONMENT'] == 'testing':
    connection_uri = env_var['DB_URL_TESTING']
else:
    connection_uri = env_var['DB_URL']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = connection_uri
CORS(app)
database = SQLAlchemy(app)
ma = Marshmallow(app)

from app.routes.users import *

from app.routes.tasks import *

if __name__ == "__main__":
    app.run()