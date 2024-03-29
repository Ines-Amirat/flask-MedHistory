from flask import Flask, request
import json
from supabase import create_client, Client

app = Flask(__name__)

url="https://hssqpmvmxjemxpnxlten.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhzc3FwbXZteGplbXhwbnhsdGVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDczODYzNDksImV4cCI6MjAyMjk2MjM0OX0.MXW1cXjLxD-lSRSRu4xV2mz7m1hJYvbwLoEtpg0c3nM"

supabase: Client = create_client(url, key)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/records_type.get')
def api_records_type_get():
    response = supabase.table('records_type').select("*").execute()
    
    return json.dumps(response.data)


@app.route('/specialties.get')
def api_specialties_get():
    response = supabase.table('specialties').select("*").execute()
    return json.dumps(response.data)



@app.route('/countries.get')
def api_countries_get():
    response = supabase.table('countries').select("*").execute()
    return json.dumps(response.data)


@app.route('/Relation.get')
def api_Relation_get():
    response = supabase.table('Relation').select("*").execute()
    return json.dumps(response.data)





@app.route('/about')
def about():
    return 'About'