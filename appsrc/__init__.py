
from flask import Flask
from libs import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask.json import JSONEncoder
from libs import variables, logs, utils
import flask_login
from flask_login import LoginManager
import uuid
from flask_session import Session 
from datetime import timedelta


logs.logger_init(filename="app.log")

app = Flask(__name__, template_folder=variables.TEMPLATES_URL, static_folder=variables.STATIC_URL) 

app.config.from_object(config.config)

db = SQLAlchemy(app)


from libs import postgres
#print(postgres.retrieveCustomerDetails('ABC-1234'))
#print(postgres.subscriptionStatus('129290t5'))
#print(postgres.customerPassion('ABC-1234','1990'))
#print(postgres.retrieveCustomerOrder('00000100'))
# display db content

from appsrc import route