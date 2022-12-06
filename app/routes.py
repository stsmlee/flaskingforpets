import json
import sqlite3
from argon2 import PasswordHasher
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for, Markup)
from wtforms.validators import Length, NoneOf, ValidationError, StopValidation, Optional
from app import app, forms
from app.pet_helper import pet_info, squordle
from flask_session import Session
from app.sneaky import get_session_str
from datetime import datetime
import copy

pet_types_dict = pet_info.types_dict

def get_db_connection():
    conn = sqlite3.connect('database.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {field} field - {error}", 'error')

def flash_basic_error(form_field):
    for error in form_field.errors:
        flash(error, 'error')

def login_errors(login_form):
    if login_form.username.errors:
        for error in login_form.username.errors:
            flash(error, 'error')
    else:
        for error in login_form.password.errors:
            flash(error, 'error') 

def register_user_db(username, password, nickname=None):
    username = username.lower()
    ph = PasswordHasher()
    hash = ph.hash(password)
    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, password, nickname) VALUES (?,?,?)', (username,hash,nickname))
    if nickname:
        name = nickname
    else:
        name = username
    flash(f'Successfully registered. Welcome, {name}!', 'notice')
    conn.commit()
    conn.close()

def update_user_pw_nickname_db(username,password,nickname):
    username = username.lower()
    ph = PasswordHasher()
    hash = ph.hash(password)
    conn = get_db_connection()
    conn.execute('UPDATE users SET password = ?, nickname = ? WHERE username = ?', (hash,nickname,username))
    flash(f'Your account changes have been saved, {nickname}.', 'notice')
    conn.commit()
    conn.close()

def update_user_pw_db(username,password):
    username = username.lower()
    ph = PasswordHasher()
    hash = ph.hash(password)
    conn = get_db_connection()
    conn.execute('UPDATE users SET password = ? WHERE username = ?', (hash,username))
    flash('Your password has been updated.', 'notice')
    conn.commit()
    conn.close()

def update_user_nickname_db(username,nickname):
    username = username.lower()
    conn = get_db_connection()
    conn.execute('UPDATE users SET nickname = ? WHERE username = ?', (nickname,username))
    flash(f'Your nickname has been updated, {nickname}.', 'notice')
    conn.commit()
    conn.close()

def logged_in():
    if 'user_token' in session:
        return True
    return False

def get_user_id():
    conn = get_db_connection()
    user = conn.execute('SELECT user_id FROM session_table WHERE user_token = ?', (session['user_token'],)).fetchone()
    conn.close()
    return user[0]

def get_username():
    conn = get_db_connection()
    username = conn.execute('SELECT username FROM users WHERE id = ?', (get_user_id(),)).fetchone()
    conn.close()
    return username[0]

def get_user_nickname():
    conn = get_db_connection()
    names = conn.execute('SELECT username, nickname FROM users WHERE id = ?', (get_user_id(),)).fetchone()
    if names['nickname']:
        name = names['nickname']
    else:
        name = names['username']
    return name

def set_user_timezone(tz):
    conn = get_db_connection()
    conn.execute('UPDATE users SET timezone = ? WHERE id =?', (tz, get_user_id()))
    conn.commit()
    conn.close()

def get_user_timezone():
    conn = get_db_connection()
    res = conn.execute('SELECT timezone FROM users WHERE id = ?', (get_user_id(),)).fetchone()
    conn.close()
    if res:
        return res[0]
    else:
        return res

def login_session_db(username):
    session['user_token'] = get_session_str()
    username = username.lower()
    now = datetime.now()
    conn = get_db_connection()
    user_id = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    user_id = user_id['id']
    conn.execute('INSERT INTO session_table (user_token, user_id, age) VALUES (?,?,?)', (session['user_token'], user_id, now))
    conn.commit()
    conn.close()

def active_session(token):
    conn = get_db_connection()
    check = conn.execute('SELECT * FROM session_table WHERE user_token = ?', (token,)).fetchone()
    return check
    
def logout_db():
    conn = get_db_connection()
    conn.execute('DELETE FROM session_table WHERE user_token = ?', (session['user_token'],))
    conn.commit()
    conn.close()
    session.clear()

def save_search(savename,params):
    conn = get_db_connection()
    conn.execute('INSERT INTO saves (savename, params, user_id) VALUES (?,?,?)', (savename, params, get_user_id()))
    conn.commit()
    conn.close()

def update_search(savename,params):
    conn = get_db_connection()
    conn.execute('UPDATE saves SET params = ? WHERE savename = ? and user_id = ?', (params, savename, get_user_id()))
    conn.commit()
    conn.close()

def save_results_db(results, savename):
    conn = get_db_connection()
    conn.execute('UPDATE saves SET results = ? WHERE savename = ? AND user_id = ?', (results, savename, get_user_id()))
    conn.commit()
    conn.close()

def get_savenames():
    conn = get_db_connection()
    res = conn.execute('SELECT savename FROM saves WHERE user_id = ?', (get_user_id(),)).fetchall()
    conn.close()
    results = [row['savename'] for row in res]
    return results

def get_params(savename):
    conn = get_db_connection()
    res = conn.execute('SELECT params FROM saves WHERE savename = ? AND user_id = ?', (savename,get_user_id())).fetchone()
    conn.close()
    return res[0]

def get_savenames_params():
    conn = get_db_connection()
    res = conn.execute('SELECT savename,params FROM saves WHERE user_id = ?', (get_user_id(),)).fetchall()
    conn.close()
    names_params = {}
    for row in res:
        param_list = []
        savename = row['savename']
        params = json.loads(row['params'])
        for k, v in params.items():
            k = k.replace('_', ' ')
            if isinstance(v, str):
                v = v.replace(',', ', ')
            if v == 1 and k != 'distance':
                v = 'yes'
            if k == 'limit':
                k = 'results per page'      
                continue      
            param_list.append(k + ': ' + str(v))
        names_params[savename] = ' | '.join(param_list).lower()
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
        conn.execute('DELETE FROM saves WHERE user_id = ? AND savename = ?', (get_user_id(), savename))
    conn.commit()
    conn.close()
    flash('Selected saved searches successfully cleared.', 'notice')

def check_savecount(form,field):
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT (*) FROM saves WHERE user_id = ?', (get_user_id(),)).fetchone()
    conn.close()
    count = count[0]
    if count >= 20:
        raise StopValidation(Markup('You have reached the maximum number of saved searches (20), please go to <a href="/manageaccount">Manage Your Account</a> to make space for more.'))

def get_token():
    token = pet_info.get_token()
    auth = "Bearer " + token
    pet_info.header = {"Authorization": auth}

def try_token():
    try: 
        get_token()
    except: 
        flash('Petfinder is currently down, please try again later.', 'response error')
        return redirect(url_for('index'))

def sort_limit_options(limit):
    options = [5,10,15,20,25,30]
    options.remove(limit)
    options.insert(0, limit)
    return options
        
@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    login_form = forms.LoginForm()
    reuse_form = forms.ReuseForm()
    if logged_in():  
        if not active_session(session['user_token']):
            logout_db()
            return redirect(url_for('index'))
        res = get_savenames()
        reuse_form.savename.choices = res
        name = get_user_nickname()
        if reuse_form.validate_on_submit():
            payload = get_params(reuse_form.savename.data)
            payload = json.loads(payload)
            type = payload['type']
            return redirect(url_for('search_saved', payload=json.dumps(payload), type = type, page=1, savename = reuse_form.savename.data))   
        return render_template('index.html', pet_types_dict = pet_types_dict, re_form = reuse_form, name = name)
    if login_form.validate_on_submit():
        login_session_db(login_form.username.data)
        name = get_user_nickname()
        flash(f"Login successful. Welcome back, {name}.", 'notice')
        return redirect(url_for('index'))
    else:
        login_errors(login_form)
    return render_template('index.html', pet_types_dict = pet_types_dict, form=login_form)

@app.route('/animals/<type>', methods=["GET", "POST"])
def animals(type):
    my_form = forms.FilterForm()
    my_form.breed1.choices = ['N/A'] + pet_types_dict[type]['Breeds']
    my_form.breed2.choices = my_form.breed1.choices
    my_form.color.choices = ['N/A'] + pet_types_dict[type]['Colors']
    my_form.coat.choices = ['N/A'] + pet_types_dict[type]['Coats']
    if logged_in():
        savenames = get_savenames()
        savestring = ', '.join(savenames)
        err_msg = 'Please make sure to use a unique savename, not any of these: ' + savestring
        my_form.savename.validators = [check_savecount, NoneOf(savenames, message=err_msg), Length(min=3,max=20), Optional()]
    if my_form.validate_on_submit():
        payload = pet_info.build_params(my_form.data, type)
        if my_form.savename.data:
            save_search(my_form.savename.data, json.dumps(payload))
            return redirect(url_for('search_saved', type=type, payload=json.dumps(payload), page=1, savename=my_form.savename.data))
        return redirect(url_for('search', type=type, payload=json.dumps(payload), page=1))
    elif logged_in() and my_form.savename.errors:
        flash_basic_error(my_form.savename)
    return render_template('animal.html', form = my_form, type=type, login = logged_in())

@app.route('/animals/<type>/page<int:page>/<payload>', methods=["GET", "POST"])
def search(type,payload,page):
    try_token()
    payload = json.loads(payload)
    payload = pet_info.return_the_slash(payload)
    payload['page'] = page
    limit = payload['limit']
    limit_options = sort_limit_options(limit)
    res_json = pet_info.get_request(payload)
    if isinstance(res_json, int):
        flash(f'There was an issue with Petfinder, please try again later. Status code {str(res_json)}.', 'response error')
        return redirect(url_for('index'))
    if not res_json:
        return render_template('no_results.html', type=type)
    if request.method == 'POST' and request.form.get('limit'):
        payload['limit'] = int(request.form.get('limit'))
        return redirect(url_for('search', type=type, payload=json.dumps(payload), page=page))
    return render_template('result.html', payload=json.dumps(payload),res= pet_info.parse_res_animals(res_json['animals']), type=type, pag = pet_info.parse_res_pag(res_json['pagination']), limit_options=limit_options)

@app.route('/animals/<type>/page<int:page>/<payload>/<savename>', methods=["GET", "POST"])
def search_saved(type,payload,page,savename):
    try: 
        get_token()
    except: 
        flash('Petfinder is currently down, please try again later.', 'response error')
        return redirect(url_for('index'))
    payload = json.loads(payload)
    payload = pet_info.return_the_slash(payload)
    payload['page'] = page
    limit = payload['limit']
    limit_options = sort_limit_options(limit)
    res_json = pet_info.get_request(payload)
    if isinstance(res_json, int):
        flash(f'There was an issue with Petfinder, please try again later. Status code {str(res_json)}.', 'response error')
        return redirect(url_for('index'))
    if not res_json:
        return render_template('no_results.html', type=type)
    results = pet_info.save_results(res_json, saved_dict={})
    save_results_db(json.dumps(results), savename)
    if request.method == 'POST' and request.form.get('limit'):
        payload['limit'] = int(request.form.get('limit'))
        update_search(savename, json.dumps(payload))
        return redirect(url_for('search_saved', type=type, payload=json.dumps(payload), page=page, savename=savename))
    return render_template('result.html', payload=json.dumps(payload),res= pet_info.parse_res_animals(res_json['animals']), type=type, pag = pet_info.parse_res_pag(res_json['pagination']), limit_options=limit_options, savename=savename)

@app.route('/whatsnews')
def check_updates():
    if get_savenames():
        try_token()
        results = pet_info.check_for_new_results(get_user_id())
        if isinstance(results, int):
            flash(f'There was an issue with Petfinder, please try again later. Status code {str(results)}.', 'response error')
            return redirect(url_for('index'))
        elif not results: 
            flash("Nothing new for you, I'm afraid. Maybe try a new search!", 'notice')
        else:
            for savename in results:
                flash(f'{savename} has new results!', 'notice')
    else:
        flash('You actually don\'t have any saved searches right now.', 'notice')
    return redirect(request.referrer)   

@app.route('/register', methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        register_user_db(form.username.data,form.password.data, form.nickname.data)
        login_session_db(form.username.data)
        return redirect(url_for('index'))
    else:
        flash_errors(form)
    return render_template('register.html', form = form)

@app.route('/logout')
def logout():
    logout_db()
    flash('Successfully logged out.', 'notice')
    return redirect(url_for('index'))

@app.route('/manageaccount', methods=["GET", "POST"])
def manage_account():
    change_form = forms.ChangePasswordForm()
    saved = get_savenames_params()
    if request.method == 'POST' and request.form.getlist('savenames'):
        req_list = request.form.getlist('savenames')
        delete_save(req_list)
        return redirect(url_for('manage_account'))
    if change_form.validate_on_submit():
        username = change_form.username.data
        nickname = change_form.nickname.data
        new_password = change_form.new_password.data
        if nickname and new_password:
            update_user_pw_nickname_db(username, new_password, nickname)
        elif nickname:
            update_user_nickname_db(username, nickname)
        else:
            update_user_pw_db(username, new_password)
        return redirect(url_for('manage_account'))
    else:
        flash_errors(change_form)
    return render_template('manage.html', saves=saved, change_form = change_form)

@app.route('/deleteaccount')
def delete_account():
    return render_template('delete.html')

@app.route('/deleteaccount/confirm')
def confirm_delete():
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (get_user_id(),))
    conn.commit()
    conn.close()
    session.clear()
    flash('Account successfully deleted.', 'notice')
    return redirect(url_for('index'))

@app.route('/squordle', methods=['GET', 'POST'])
def puzzle():
    return render_template('squordle.html')

@app.route('/squordle/random', methods=['GET', 'POST'])
def random_puzzle():
    puzzle_id = squordle.get_random_puzzle()
    return redirect(url_for('play_puzzle', puzzle_id=puzzle_id))

def flash_puzzle_error(form):
    msg_set = set()
    for field, errors in form.errors.items():
        for error in errors:
            msg_set.add(error)
    for msg in msg_set:
        flash(msg, 'puzzle error')

def build_word(form_data):
    guess = ''
    for fieldname,value in form_data.items():
        if 'csrf' not in fieldname:
            guess+=value
    guess = guess.upper()
    return guess

def valid_word(word):
    conn = get_db_connection()
    first_char = word[0]
    res = conn.execute(f'''SELECT * FROM {first_char} WHERE word = "{word.lower()}"''').fetchone()
    if res:
        return True

@app.route('/squordle/play/<int:puzzle_id>/', methods=['GET', 'POST'])
def play_puzzle(puzzle_id):
    form = forms.GuessWordForm()
    puzzle = squordle.choices[puzzle_id]
    # trim form to word length
    diff_len = 7 - len(puzzle.word)
    if diff_len > 0:
        del form.l6
    if diff_len == 2:
        del form.l5
    if request.method == "POST":
        if form.validate():
            guess = build_word(form.data)
            if valid_word(guess):
                squordle.check_guess(guess, puzzle)
            else:
                flash('Invalid word', 'puzzle error')
        else:
            flash_puzzle_error(form)
        return redirect(url_for('play_puzzle', puzzle_id=puzzle_id))
    return render_template('squordle_play.html', puzzle=puzzle, guesses=puzzle.evals, form=form)
