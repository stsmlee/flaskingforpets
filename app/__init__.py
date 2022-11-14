from flask import Flask
# , session
from app.sneaky import secret
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = secret

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from app import routes