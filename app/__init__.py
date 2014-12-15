
from flask import Flask

app = Flask(__name__)
app.config['MAP_FILE'] = 'map.json'
app.config['WTF_CSRF_ENABLED'] = False

from app import views

def change_map_file(map_file):
    views.mun.change_map_file(map_file)
    if map_file != 'map.json':
        views.mun.load_doc_map(path_prefix = views.mun.PATH_TO_XML_FILES)