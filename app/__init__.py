from flask import Flask
from app.sneaky import secret


my_app = Flask(__name__)
my_app.config["SECRET_KEY"] = secret

from app import routes