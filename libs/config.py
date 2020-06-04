import os, redis
from libs import variables
basedir = os.path.abspath(os.path.dirname(__file__))

class config(object):
    SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    APPNAME = os.getenv("APPNAME", "Cleston Hyperconnected Enterprise")


