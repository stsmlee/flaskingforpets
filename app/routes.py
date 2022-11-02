from app import forms, app
from flask import Flask, render_template, redirect, url_for, session, flash
from flask_session import Session
import json
from app.pet_helper import pet_info
from app import forms
import sqlite3
from wtforms.validators import NoneOf, Length

pet_types_dict = pet_info.get_types_dict()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def logged_in():
    if 'username' in session:
        return True
    return False

def check_user(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?',
                        (username,)).fetchone()
    if user is None:
        conn.execute('INSERT INTO users (username) VALUES (?)',
            (username,))
        conn.commit()
    conn.close()
    return

def get_user_id(username):
    conn = get_db_connection()
    userid = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return userid['id']

def save_search(savename,params):
    conn = get_db_connection()
    # conn.execute('INSERT OR REPLACE INTO saves (savename, params, user_id) VALUES (?,?,?)', (savename, params, session['user id']))
    try:
        conn.execute('INSERT INTO saves (savename, params, user_id) VALUES (?,?,?)', (savename, params, session['user id']))
        conn.commit()
    except sqlite3.IntegrityError:
        print('Needs a unique savename.')
    conn.close()

def get_savenames():
    conn = get_db_connection()
    res = conn.execute('SELECT savename FROM saves WHERE user_id = ?', (session['user id'],)).fetchall()
    conn.close()
    results = [row['savename'] for row in res]
    return results

def delete_db():
    pass

def get_params(savename):
    conn = get_db_connection()
    res = conn.execute('SELECT params FROM saves WHERE savename = ? AND user_id = ?', (savename, session['user id'])).fetchone()
    conn.close()
    return res[0]

def base_html():
    if logged_in():
        return 'base_logged_in.html'
    return 'base.html'

@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    login_form = forms.LoginForm()
    reuse_form = forms.ReuseForm()
    if login_form.validate_on_submit():
        session['username'] = login_form.username.data
        check_user(session['username'])
        session['user id'] = get_user_id(session['username'])
        return redirect(url_for('index'))
    if logged_in():  
        session['user id'] = get_user_id(session['username'])
        res = get_savenames()
        reuse_form.savename.choices = res
    if reuse_form.validate_on_submit():
        payload = get_params(reuse_form.savename.data)
        payload = json.loads(payload)
        type = payload['type']
        return redirect(url_for('search', payload=json.dumps(payload), type = type, page=1))        
    if logged_in():
        return render_template('index.html', pet_types_dict = pet_types_dict, username=session['username'], base_html='base_logged_in.html', re_form = reuse_form)
    return render_template('index.html', pet_types_dict = pet_types_dict, form=login_form, base_html='base.html')

@app.route('/logout')
def logout():
    # session.pop('username', None)
    session.clear()
    return redirect(url_for('index'))

@app.route('/animals/<type>', methods=["GET", "POST"])
def animals(type):
    my_form = forms.FilterForm()
    my_form.breed1.choices = ['N/A'] + pet_types_dict[type]['Breeds']
    my_form.breed2.choices = my_form.breed1.choices
    my_form.color.choices = ['N/A'] + pet_types_dict[type]['Colors']
    my_form.coat.choices = ['N/A'] + pet_types_dict[type]['Coats']
    my_form.savename.validators = [NoneOf(get_savenames()), Length(max=20)]
    if my_form.validate_on_submit():
        payload = pet_info.build_params(my_form.data, type)
        if my_form.savename.data:
            save_search(my_form.savename.data, json.dumps(payload))
        return redirect(url_for('search', type=type, payload=json.dumps(payload), page=1))
    return render_template('animal.html', form = my_form, type=type, base_html = base_html(), login = logged_in())

@app.route('/animals/<type>/page<int:page>/<payload>')
def search(type,payload,page):
    payload = json.loads(payload)
    payload['page'] = page
    res_json = pet_info.get_request(payload)
    if not res_json:
        return render_template('no_results.html', type=type)
    return render_template('result.html', payload=json.dumps(payload),res= pet_info.parse_res_animals(res_json['animals']), type=type, pag = pet_info.parse_res_pag(res_json['pagination']), base_html=base_html())




