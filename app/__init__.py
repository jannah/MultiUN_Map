
from flask import Flask

app = Flask(__name__)
from app import views
app.config['WTF_CSRF_ENABLED'] = False
