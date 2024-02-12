from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/records.type')
def get_record_types():
    data=[
    {'id':1,'name':'Medical Consultation'},
    {'id':2,'name':'Analyse'},
    ]
    return json.dumps(data)

@app.route('/doctors.list')
def get_list_doctors():
    data=[
    {'id':1,'name':'Dr Amirat','address':'ABC'},
    {'id':2,'name':'Dr Backouche','address':'ABCbac'},
    ]
    return json.dumps(data)


@app.route('/about')
def about():
    return 'About'