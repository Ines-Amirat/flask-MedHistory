
import base64
import datetime
import io
import logging
from PIL import Image
from flask import Flask,request,jsonify
import json
import httpx
from pydantic_core import Url
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import base64
from supabase import create_client, Client
import os


app = Flask(__name__)

#allows to start integrating Supabase features into Flask application.
SUPABASE_URL="https://ghwerggdepsautiaodrd.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdod2VyZ2dkZXBzYXV0aWFvZHJkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwNzA3NzgyMSwiZXhwIjoyMDIyNjUzODIxfQ.oy8j8ENqbx1gge8wohDrXStQqD7LH6IDj421QZgLTa0"
# Create a client to interact with the database
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
timeout = httpx.Timeout(10.0, read=60.0)

client = httpx.Client(timeout=timeout)




@app.route('/')
def home():
    return 'Hello, Flask with Supabase!'

@app.route('/records.type')
def get_doctor_list():
    response = supabase.table('records_type').select("*").execute()
    return json.dumps(response.data)

#fetch data from a table named 'countries'
@app.route('/countries.get')
def api_countries_get():
    response = supabase.table('countries').select("*").execute()
    return json.dumps(response.data)

@app.route('/specialties.get')
def api_specialties_get():
    response = supabase.table('specialties').select("*").execute()
    return json.dumps(response.data)

@app.route('/relations.get')
def api_relations_get():
    response = supabase.table('relations').select("*").execute()
    return json.dumps(response.data)

@app.route('/wilaya.get')
def api_wilaya_get():
    response = supabase.table('wilaya').select("*").execute()
    return json.dumps(response.data)

@app.route('/doctor.get')
def api_doctor_get():
    # Get the 'specialty' query parameter from the URL
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=1000, type=int)  # or any default limit
    specialty = request.args.get('specialty', default=None, type=str)
    name = request.args.get('name', default=None, type=str)
    address = request.args.get('address', default=None, type=str)
    """if specialty_param:
        response = supabase.table('doctors').select("*").eq('Specialty', specialty_param).execute()
    else:
        response = supabase.table('doctors').select("*").execute()"""
    
    # Calculate offset
    offset = (page - 1) * limit
    # Start building the query
    query = supabase.table('doctors').select("*")

    # Filter by name if it's provided
    if name:
        query = query.ilike('Name', f'%{name}%')
    
    # Filter by specialty if it's provided
    if specialty:
        query = query.ilike('Specialty', f'%{specialty}%')
    
    # Filter by region contained within the Address if it's provided
    if address:
        query = query.ilike('Address', f'%{address}%')

     # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute the query
    response = query.execute()

    return json.dumps(response.data)

def scrape_doctors(doctor_name, specialty, region):
    # Set up ChromeDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()),options=chrome_options)
    #service = Service(executable_path=ChromeDriverManager().install())
    #driver = webdriver.Chrome(service=service)

    # Build the URL using the arguments
    url = 'https://www.med.tn/docteur-algerie'
    if specialty:
        url += f'/{specialty}'
    if region:
        url += f'/{region}'
    if doctor_name:
        url += f'/recherche/{doctor_name}'
    
    # Navigate to the website
    driver.get(url)

    # Wait for the elements to load
    wait = WebDriverWait(driver, 30)
    doctor_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "card-doctor-block")))

    # Store the data in a list
    doctors_data = []

    # Loop through each doctor element and extract the information
    for doctor_element in doctor_elements:
        try:
            name = doctor_element.find_element(By.CLASS_NAME, "list__label--name").text
            specialty = doctor_element.find_element(By.CLASS_NAME, "list__label--spee").text
            address = doctor_element.find_element(By.CLASS_NAME, "list__label--adr").text
            doctors_data.append({"Name": name, "Specialty": specialty, "Address": address})
        except NoSuchElementException:
            print("Some elements could not be found. Skipping this entry.")
            continue
        
    # Clean up
    driver.quit()

    # Convert data to JSON and return
    return doctors_data

@app.route('/recordinfo.set', methods=['POST'])
def api_endpoint_post_add_info_record():
    # Extract data from the form
    data = {
        'title': request.form.get('title'),
        'recordtype': request.form.get('recordType'),
        'name': request.form.get('doctor'),
        'sp': request.form.get('sp'),
        'date': request.form.get('date'),
        'des': request.form.get('des'),
        'user_id':request.form.get('userId'),
    }
    # Insert data into Supabase table (replace 'your_table_name' with the actual table name)
    #response = supabase.table('records').insert(data).execute()

    try:
        response = supabase.table('records').insert(data).execute()
        print(response)
        # Assuming the response object has a method or property to get the data
        if hasattr(response, 'data') and response.data:  # Check if the response has a data attribute and it's not empty
            print("ee")
            inserted_record_id = response.data[0].get('id')
            print(inserted_record_id)
            return jsonify({'message': 'Record added successfully', 'record_id': inserted_record_id}), 201
        else:
            return jsonify({'error': 'Failed to add the record', 'details': 'No data returned'}), 400
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    

def compress_image(file):
    img = Image.open(file)
    img_io = io.BytesIO()
    #img_format = "JPEG" if img_format == "JPEG" else "JPG"
    img.save(img_io,format=img.format,quality=10)
    img_io.seek(0)

    return img_io


@app.route('/upload_images', methods=['POST'])
def upload_images():
    if 'userId' not in request.form:
        return jsonify(error='No userId provided'), 400
    user_id = request.form['userId']
    print(user_id)

    if 'record_id' not in request.form:
        return jsonify(error='No recordId provided'), 400
    record_id = request.form['record_id']
    print(record_id)

    if 'file' not in request.files:
        return jsonify(error='No file part'), 400
    files = request.files.getlist('file')
    print(files)
    
    if not files or any(file.filename == '' for file in files):
        return jsonify(error='No selected image'), 400

    uploaded_files_urls = []
    bucket_name = 'image'  # Your bucket name here
    
    for file in files:
        filename = secure_filename(file.filename)
        file_bytes = compress_image(file).read()  # Read the file in bytes
        
        upload_path = f'{user_id}/{record_id}/uploads/{filename}'

        try:
            # Upload the file to Supabase
            response = supabase.storage.from_(bucket_name).upload(upload_path, file_bytes)
            print(response)
            if response.status_code in range(200, 300):
                print("Upload successful")
                # Obtain the file URL if necessary
                file_url = supabase.storage.from_(bucket_name).get_public_url(upload_path)
                #file_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{upload_path}"
                print(file_url)
                uploaded_files_urls.append(file_url)
            else:
                print("Failed to upload, no key in result")
                return jsonify(error='Failed to upload to Supabase'), 500
        except Exception as e:
            print("Exception during upload:", e)
            return jsonify(error=str(e)), 500

    if uploaded_files_urls:
        return jsonify(urls=uploaded_files_urls), 200
    else:
        return jsonify(error='Failed to upload images'), 400

@app.route('/send_email', methods=['POST'])
def sendEmail():
    print("oioioio")
    if 'user_id' not in request.form:
        return jsonify(error='No userId provided'), 400
    user_id = request.form['user_id']
    print(user_id)

    if 'record_id' not in request.form:
        return jsonify(error='No recordId provided'), 400
    record_id = request.form['record_id']
    print(record_id)

    if 'email' not in request.form:
        return jsonify(error='No recordId provided'), 400
    email = request.form['email']
    print(email)

    # construct  email message
    msg = Message('Record Information', sender='noreply@mail.medhistory.app', recipients=[email])
    #msg.body = f'This email is to inform you about record ID: {record_id} for user ID: {user_id}.'
    msg.body = f'https://html-starter-iota-one.vercel.app/?record_id={record_id}&user_id={user_id}'

    
    # Send the email
    mail.send(msg)

    return jsonify(message='Email sent successfully'), 200
    

@app.route('/scrape')
def scrape():
    # Get parameters from URL query string
    doctor_name = request.args.get('name', default="", type=str)
    specialty = request.args.get('sp', default="", type=str)
    region = request.args.get('rg', default="", type=str)

    # Call the scrape function
    result = scrape_doctors(doctor_name, specialty, region)

    # Return the result as a JSON response
    return json.dumps(result)








@app.route('/about')
def about():
    return 'About'



@app.route('/fetch_record_and_photos', methods=['POST'])
def fetch_record_and_photos():
    # Extraire les données JSON de la requête
    data = request.get_json()
    user_id = data.get('user_id')
    record_id = data.get('record_id')
    
    if not user_id or not record_id:
        return jsonify({'error': 'Missing user_id or record_id'}), 400
    
    try:
        # Récupérer les informations du dossier médical
        record_info_response = supabase.table('records').select('*').eq('id', record_id).execute()
        record_info = record_info_response.data
        
        # Récupérer les photos associées au dossier médical
        # Assurez-vous de remplacer 'bucket_name' par le nom de votre bucket
        photos_response = supabase.storage.from_('image').list(f'{user_id}/{record_id}')
        photos_info = photos_response.data
        
        # Construire la réponse
        response = {
            'record_info': record_info,
            'photos_info': photos_info
        }
        
        return jsonify(response), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to fetch data from Supabase'}), 500













"""
app = Flask(__name__)

url="https://hssqpmvmxjemxpnxlten.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhzc3FwbXZteGplbXhwbnhsdGVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDczODYzNDksImV4cCI6MjAyMjk2MjM0OX0.MXW1cXjLxD-lSRSRu4xV2mz7m1hJYvbwLoEtpg0c3nM"

supabase: Client = create_client(url, key)
"""







"""

@app.route('/upload_images', methods=['POST'])
def upload_images():
    # Vérifiez si la partie 'image' est dans la requête
    if 'image' not in request.files:
        return {'error': 'No image part'}, 400

    # Récupérez le fichier de la requête
    file = request.files['image']

    # Vérifiez si un fichier a été sélectionné
    if file.filename == '':
        return {'error': 'No selected image'}, 400

    if file:
        filename = secure_filename(file.filename)
        file_bytes = file.read()  # Lire le fichier en bytes

        print("Avant l'upload")

        try:

            # Remplacez 'your-bucket-name' avec le nom de votre bucket Supabase
            bucket_name = 'photos'
            result = supabase.storage.from_(bucket_name).upload('uploads/' + filename, file_bytes)
            print("Après l'upload :", result)



            # Vérifiez si la clé 'Key' est dans le résultat
            if 'Key' in result:
                # Vous pouvez obtenir l'URL du fichier si nécessaire
                file_url = supabase.storage.from_(bucket_name).get_public_url('uploads/' + filename).data.get('publicURL')
                print("URL du fichier :", file_url)
                return {'url': file_url}, 200
            else:
                print("Échec de l'upload, pas de clé dans le résultat")
                return {'error': 'Failed to upload to Supabase'}, 500
        except Exception as e:
            print("Exception lors de l'upload :", e)
            return {'error': str(e)}, 500
    else:
        return {'error': 'Failed to upload image'}, 400


"""
"""
if __name__ == '__main__':
    app.run(debug=True)
"""














    


       
      

      

   




    

 