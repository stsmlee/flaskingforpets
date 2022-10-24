from app import forms, my_app
from flask import Flask, render_template
import json
from app.pet_helper import pet_info
from app import forms

pet_types_dict = pet_info.get_types_dict()

@my_app.route('/')
@my_app.route('/index')
def index():
    return render_template('index.html', pet_types_dict = pet_types_dict)

@my_app.route('/animals/<type>', methods=["GET", "POST"])
def animals(type):
    my_form = forms.TypeForm()
    return render_template('animal.html', form = my_form, type=type)
    # if my_form.validate_on_submit():
    #     return redirect(url_for("animals", my_form.data))
