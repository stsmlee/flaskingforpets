from flask import Flask
from argon2 import PasswordHasher
import requests
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, RadioField, BooleanField, SelectField, IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length, NoneOf, ValidationError, StopValidation

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def password_check(form,field):
    password = form.password.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')

def username_check(form,field):
    username = form.username.data
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?',
                        (username,)).fetchone()
    conn.close()
    if user:
        raise StopValidation('This username is already in use. If it is yours, perhaps try to log in with it, or else use a unique username.')

def verify_user(form,field):
    username = form.username.data
    conn = get_db_connection()
    res = conn.execute('SELECT username FROM users WHERE username = ?', (username,)).fetchone()
    if res is None:
        raise StopValidation('Username does not exist, please double check your entry or register a new account.')

def verify_password(form,field):
    ph = PasswordHasher()
    username = form.username.data
    password = form.password.data
    conn = get_db_connection()
    res = conn.execute('SELECT password FROM users WHERE username = ?', (username,)).fetchone()
    try:
        ph.verify(res['password'], password)
    except:
        raise ValidationError('Password incorrect.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators= [InputRequired(), Length(min=1, max=20), verify_user])
    password = PasswordField('Password', validators= [InputRequired(), verify_password])
    submit = SubmitField('Login',render_kw= {'class': 'submit_button'})

class RegisterForm(FlaskForm):
    username = StringField('Username', validators= [InputRequired(), Length(min=1, max=20), username_check])
    password = PasswordField('Password', validators= [InputRequired(), password_check])
    submit = SubmitField('Register', render_kw= {'class': 'submit_button'})

class ReuseForm(FlaskForm):
    savename = SelectField('Saved Searches', render_kw= {'class': 'form_font'})
    submit = SubmitField('Let\'s Go!', render_kw= {'class': 'submit_button'})

class FilterForm(FlaskForm):
    breed1 = SelectField('Breed1')
    breed2 = SelectField('Breed2')
    color = SelectField('Color')
    coat = SelectField('Coat')
    gender = SelectField('Gender', choices = ['N/A', 'Male', 'Female'])
    baby = BooleanField('Baby')   
    young = BooleanField('Young')
    adult = BooleanField('Adult')
    senior = BooleanField('Senior')
    small = BooleanField('Small')
    medium = BooleanField('Medium')
    large = BooleanField('Large')
    xlarge = BooleanField('X-Large')
    children = BooleanField('Good with Children')
    dogs = BooleanField('Good with Dogs')
    cats = BooleanField('Good with Cats')
    zipcode = StringField('Zipcode (Required)', default = '11101', validators = [InputRequired()])
    distance = IntegerField('Distance (Miles)', default = 30, validators = [NumberRange(min=0, max=500), InputRequired()])
    savename = StringField('Save Name', validators=[Length(min=3)])
    submit = SubmitField('Submit', render_kw= {'class': 'submit_button'})

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class DeleteSavesForm(FlaskForm):
    saves = MultiCheckboxField('Saved Searches')
    submit = SubmitField('Delete', render_kw= {'class': 'submit_button'})