from app import forms, app
from flask import Flask, render_template
import json
from app.pet_helper import pet_info
from app import forms

pet_types_dict = pet_info.get_types_dict()
pet_types_list = [pet_type for pet_type in pet_types_dict.keys()]

# pet_types_list = [(count, val) for count, val in enumerate(pet_types_dict.keys())]



@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', pet_types_dict = pet_types_dict)

@app.route('/animals/<type>', methods=["GET", "POST"])
def animals(type):
    my_form = forms.BreedForm()
    my_form.choice.choices = pet_types_dict[type]['Breeds']
    return render_template('animal.html', form = my_form, type=type, list=pet_types_list, breeds = pet_types_dict[type]['Breeds'])
    # if my_form.validate_on_submit():
    #     return redirect(url_for("animals", my_form.data))
