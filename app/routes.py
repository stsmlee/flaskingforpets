from app import app
from flask import Flask, render_template
import json
from app.pet_helper import pet_info

pet_types_dict = pet_info.get_types_dict()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', pet_types_dict = pet_types_dict)

@app.route('/animals/<type>')
def animals(type):
    return type