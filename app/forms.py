from flask import Flask
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, BooleanField, SelectField, IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length, NoneOf

class LoginForm(FlaskForm):
    username = StringField('Username', validators= [InputRequired(), Length(min=1, max=20)])
    submit = SubmitField('Submit')

class ReuseForm(FlaskForm):
    savename = SelectField('Saved Searches', validators= [InputRequired()])
    submit = SubmitField('Let\'s Go!')

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
    savename = StringField('Save Name')
    submit = SubmitField('Submit')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class DeleteSavesForm(FlaskForm):
    saves = MultiCheckboxField('Saved Searches')
    submit = SubmitField('Delete')