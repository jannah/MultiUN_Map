from flask import  url_for, render_template
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import Required
from app import app


class SearchForm(Form):
    q = StringField('search-q', validators=[Required()])