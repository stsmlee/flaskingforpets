from app import forms, app
from flask import Flask, render_template, redirect, url_for, session, flash
from flask_session import Session
import json
from app.pet_helper import pet_info
import sqlite3
from wtforms.validators import NoneOf, Length, ValidationError
from argon2 import PasswordHasher

pet_types_dict = pet_info.get_types_dict()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {field} field - {error}", 'error')

def register_user_db(username, password):
    ph = PasswordHasher()
    hash = ph.hash(password)
    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, password) VALUES (?,?)', (username,hash))
    flash(f'Successfully registered. Welcome {username}!', 'notice')
    conn.commit()
    conn.close()

def logged_in():
    if 'username' in session:
        return True
    return False

def get_user_id(username):
    conn = get_db_connection()
    userid = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return userid['id']

def save_search(savename,params):
    conn = get_db_connection()
    conn.execute('INSERT INTO saves (savename, params, user_id) VALUES (?,?,?)', (savename, params, session['user id']))
    conn.commit()
    conn.close()

def save_results_db(results, savename):
    conn = get_db_connection()
    conn.execute('UPDATE saves SET results = ? WHERE savename = ? AND user_id = ?', (results, savename, session['user id']))
    conn.commit()
    conn.close()

def get_savenames():
    conn = get_db_connection()
    res = conn.execute('SELECT savename FROM saves WHERE user_id = ?', (session['user id'],)).fetchall()
    conn.close()
    results = [row['savename'] for row in res]
    return results

def get_params(savename):
    conn = get_db_connection()
    res = conn.execute('SELECT params FROM saves WHERE savename = ? AND user_id = ?', (savename, session['user id'])).fetchone()
    conn.close()
    return res[0]

def get_savenames_params():
    conn = get_db_connection()
    res = conn.execute('SELECT savename,params FROM saves WHERE user_id = ?', (session['user id'],)).fetchall()
    conn.close()
    names_params = {}
    for row in res:
        parastring = str(row['params'])[1:-1]
        parastring = parastring.replace('\"', '')
        names_params[row['savename']] = parastring
    return names_params

def clean_up_req_dels(formdata):
    req_dels = []
    for selected in formdata:
        name = ''
        for l in selected:
            if l == ':':
                break
            else:
                name += l
        req_dels.append(name)
    return req_dels

def delete_save(req_list):
    conn = get_db_connection()
    for savename in req_list:
        conn.execute('DELETE FROM saves WHERE user_id = ? AND savename = ?', (session['user id'], savename))
    conn.commit()
    conn.close()
    flash('Selected saved searches successfully cleared.', 'notice')
        
@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    login_form = forms.LoginForm()
    reuse_form = forms.ReuseForm()
    if logged_in():  
        session['user id'] = get_user_id(session['username'])
        res = get_savenames()
        reuse_form.savename.choices = res
        if reuse_form.validate_on_submit():
            payload = get_params(reuse_form.savename.data)
            payload = json.loads(payload)
            type = payload['type']
            return redirect(url_for('search_saved', payload=json.dumps(payload), type = type, page=1, savename = reuse_form.savename.data))   
        return render_template('index.html', username = session['username'], pet_types_dict = pet_types_dict, re_form = reuse_form)
    if login_form.validate_on_submit():
        # print('WE LOGGED IN')
        session['username'] = login_form.username.data
        session['user id'] = get_user_id(session['username'])
        flash("Login successful. Welcome back.", 'notice')
        return redirect(url_for('index'))
    else:
        flash_errors(login_form)  
    return render_template('index.html', pet_types_dict = pet_types_dict, form=login_form)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    flash_errors(form)
    if form.validate_on_submit():
        register_user_db(form.username.data,form.password.data)
        session['username'] = form.username.data
        return redirect(url_for('index'))
    else:
        flash_errors(form)
    return render_template('register.html', form = form)

@app.route('/animals/<type>', methods=["GET", "POST"])
def animals(type):
    my_form = forms.FilterForm()
    my_form.breed1.choices = ['N/A'] + pet_types_dict[type]['Breeds']
    my_form.breed2.choices = my_form.breed1.choices
    my_form.color.choices = ['N/A'] + pet_types_dict[type]['Colors']
    my_form.coat.choices = ['N/A'] + pet_types_dict[type]['Coats']
    if logged_in():
        savenames = get_savenames()
        my_form.savename.validators = [NoneOf(savenames), Length(max=20)]
    if my_form.validate_on_submit():
        payload = pet_info.build_params(my_form.data, type)
        if my_form.savename.data:
            save_search(my_form.savename.data, json.dumps(payload))
            return redirect(url_for('search_saved', type=type, payload=json.dumps(payload), page=1, savename=my_form.savename.data))
        return redirect(url_for('search', type=type, payload=json.dumps(payload), page=1))
    elif logged_in() and my_form.savename.errors:
        savestring = ', '.join(savenames)
        msg = 'Please make sure to use a unique savename, not any of these: ' + savestring
        flash(msg, 'error')
    return render_template('animal.html', form = my_form, type=type, login = logged_in())

@app.route('/animals/<type>/page<int:page>/<payload>/<savename>')
def search_saved(type,payload,page,savename):
    payload = json.loads(payload)
    payload = pet_info.return_the_slash(payload)
    payload['page'] = page
    res_json = pet_info.get_request(payload)
    # print(res_json)
    if isinstance(res_json, int):
        flash(f'There was an issue with Petfinder, please try again later. Status code {str(res_json)}.', 'response error')
        return redirect(url_for('index'))
    if not res_json:
        return render_template('no_results.html', type=type)
    results = pet_info.save_results(res_json, saved_dict={})
    print(len(results))
    save_results_db(json.dumps(results), savename)
    return render_template('result.html', payload=json.dumps(payload),res= pet_info.parse_res_animals(res_json['animals']), type=type, pag = pet_info.parse_res_pag(res_json['pagination']))

@app.route('/animals/<type>/page<int:page>/<payload>')
def search(type,payload,page):
    # print('MADE IT TO SEARCH')
    payload = json.loads(payload)
    payload = pet_info.return_the_slash(payload)
    payload['page'] = page
    res_json = pet_info.get_request(payload)
    if isinstance(res_json, int):
        flash(f'There was an issue with Petfinder, please try again later. Status code {str(res_json)}.', 'response error')
        return redirect(url_for('index'))
    if not res_json:
        return render_template('no_results.html', type=type)
    return render_template('result.html', payload=json.dumps(payload),res= pet_info.parse_res_animals(res_json['animals']), type=type, pag = pet_info.parse_res_pag(res_json['pagination']))

# @app.route('/clearsaves')
# def clear_saves():
#     conn = get_db_connection()
#     conn.execute('DELETE FROM saves WHERE user_id = ?', (session['user id'],))
#     conn.commit()
#     conn.close()
#     flash('Saved searches successfully cleared.', 'notice')
#     return redirect(url_for('index'))

@app.route('/manageaccount', methods=["GET", "POST"])
def manage_account():
    del_form = forms.DeleteSavesForm()
    saved = get_savenames_params()
    del_form.saves.choices = [k+': '+ str(v) for k,v in saved.items()]
    if del_form.validate_on_submit():
        req_list = clean_up_req_dels(del_form.saves.data)
        delete_save(req_list)
        return redirect(url_for('manage_account'))
    return render_template('manage.html', form=del_form)

@app.route('/logout')
def logout():
    # session.pop('username', None)
    session.clear()
    flash('Successfully logged out.', 'notice')
    return redirect(url_for('index'))