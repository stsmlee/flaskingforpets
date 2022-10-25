from app import forms, app
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from app.pet_helper import pet_info
from app import forms

pet_types_dict = pet_info.get_types_dict()
payload = {}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', pet_types_dict = pet_types_dict)

@app.route('/animals/<type>', methods=["GET", "POST"])
def animals(type):
    global payload
    my_form = forms.FilterForm()
    my_form.breed1.choices = ['N/A'] + pet_types_dict[type]['Breeds']
    my_form.breed2.choices = my_form.breed1.choices
    my_form.color.choices = ['N/A'] + pet_types_dict[type]['Colors']
    my_form.coat.choices = ['N/A'] + pet_types_dict[type]['Coats']
    if my_form.validate_on_submit():
        payload = {'type':type, 'location' : my_form.zipcode.data, 'distance' : my_form.distance.data}
        if my_form.breed1.data != 'N/A':
            payload['breed'] = my_form.breed1.data
        if my_form.breed2.data != 'N/A':
            payload['breed'] += ',' + my_form.breed2.data
        if my_form.color.data != 'N/A':
            payload['color'] = my_form.color.data
        if my_form.coat.data != 'N/A':
            payload['coat'] = my_form.coat.data
        if my_form.gender.data != 'N/A':
            payload['gender'] = my_form.gender.data
        if my_form.age.data:
            payload['age'] = ','.join(my_form.age.data)
        if my_form.size.data:
            payload['size'] = ','.join(my_form.size.data)
        if my_form.children.data:
            payload['good_with_children'] = 1
        if my_form.dogs.data:
            payload['good_with_dogs'] = 1
        if my_form.cats.data:
            payload['good_with_cats'] = 1
        return redirect(url_for('search', type=type))
    return render_template('animal.html', form = my_form, type=type)

@app.route('/animals/<type>/search')
def search(type):
    global payload
    return pet_info.get_request(payload)
    # return payload
    # return render_template('index.html')