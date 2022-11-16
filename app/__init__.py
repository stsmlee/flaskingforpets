from flask import Flask
from app.sneaky import secret
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config["SECRET_KEY"] = secret
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
csrf = CSRFProtect(app)

from app import routes