from app import forms, app
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from app.pet_helper import pet_info
from app import forms

pet_types_dict = pet_info.get_types_dict()
param_dict = {}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', pet_types_dict = pet_types_dict)

@app.route('/animals/<type>', methods=["GET", "POST"])
def animals(type):
    my_form = forms.FilterForm()
    my_form.breed1.choices = ['N/A'] + pet_types_dict[type]['Breeds']
    my_form.breed2.choices = my_form.breed1.choices
    my_form.color.choices = ['N/A'] + pet_types_dict[type]['Colors']
    my_form.coat.choices = ['N/A'] + pet_types_dict[type]['Coats']
    if my_form.validate_on_submit():
        payload = pet_info.build_params(my_form.data, type)
        return redirect(url_for('search', type=type, payload=json.dumps(payload), page=1))
    return render_template('animal.html', form = my_form, type=type)

@app.route('/animals/<type>/page<int:page>/<payload>')
def search(type,payload,page):
    payload = json.loads(payload)
    payload['page'] = page
    res_json = pet_info.get_request(payload)
    if not res_json:
        return render_template('no_results.html', type=type)
    return render_template('result.html', payload=json.dumps(payload),res= pet_info.parse_res_animals(res_json['animals']), type=type, pag = pet_info.parse_res_pag(res_json['pagination']))




