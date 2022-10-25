from flask import Flask
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, BooleanField, SelectField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, InputRequired, NumberRange

class FilterForm(FlaskForm):
    breed1 = SelectField('Breed1')
    breed2 = SelectField('Breed2')
    color = SelectField('Color')
    coat = SelectField('Coat')
    gender = SelectField('Gender', choices = ['N/A', 'Male', 'Female'])
    # baby = BooleanField('Baby')
    # young = BooleanField('Young')
    # adult = BooleanField('Adult')
    # senior = BooleanField('Senior')
    # small = BooleanField('Small')
    # medium = BooleanField('Medium')
    # large = BooleanField('Large')
    # xlarge = BooleanField('X-Large')
    age = SelectMultipleField('Age', choices = ['Baby', 'Young', 'Adult', 'Senior'] )
    size = SelectMultipleField('Size', choices = ['Small', 'Medium', 'Large', 'Xlarge'])
    children = BooleanField('Good with Children')
    dogs = BooleanField('Good with Dogs')
    cats = BooleanField('Good with Cats')
    zipcode = StringField('Zipcode (Required)', validators = [InputRequired()])
    distance = IntegerField('Distance (Miles)', default = 100, validators = [NumberRange(min=0, max=500), InputRequired()])
    submit = SubmitField('Submit')

    # 'small', 'medium', 'large', 'xlarge'