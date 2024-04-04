from flask import Flask, request
import json
from supabase import create_client, Client
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

url="https://ghwerggdepsautiaodrd.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdod2VyZ2dkZXBzYXV0aWFvZHJkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwNzA3NzgyMSwiZXhwIjoyMDIyNjUzODIxfQ.oy8j8ENqbx1gge8wohDrXStQqD7LH6IDj421QZgLTa0"

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




@app.route('/upload_images', methods=['POST'])
def upload_images():
    if 'image' not in request.files:
        return 'No image part', 400
    file = request.files['image']
    

    if file.filename == '':
        return 'No selected image', 400


    if file:
        filename = secure_filename(file.filename)
        file_bytes = file.read()  # Lire le fichier en bytes

        # Remplacez 'your-bucket-name' avec le nom de votre bucket Supabase
        bucket_name = 'profiles'
        

        print("Avant l'upload")
        try:
            # Uploadez le fichier sur Supabase
            result = supabase.storage.from_(bucket_name).upload('uploads/' + filename, file_bytes)
            print("Après l'upload :", result)

           


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

    return 'Failed to upload image', 400






    


       
      

      

   




    

 