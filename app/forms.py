from flask import Flask
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, BooleanField, SelectField
from wtforms.validators import DataRequired

class FilterForm(FlaskForm):
    breed = SelectField('Breed')
    # color = SelectField('Color')
    submit = SubmitField('Submit')