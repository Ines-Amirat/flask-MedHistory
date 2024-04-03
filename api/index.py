from flask import Flask, request
import json
from supabase import create_client, Client


from werkzeug.utils import secure_filename
import os

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


# Assurez-vous que le dossier de destination existe ou créez-le
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload_images', methods=['POST'])
def upload_images():
    # Vérifiez si la partie 'image' est présente dans la requête
    if 'image' not in request.files:
        return 'No image part', 400
    file = request.files['image']
    
    # Si l'utilisateur n'a pas sélectionné de fichier, le navigateur
    # envoie une partie sans nom de fichier
    if file.filename == '':
        return 'No selected image', 400
    if file:
        # Sécurisez le nom du fichier pour éviter les failles de sécurité
        filename = secure_filename(file.filename)
        # Sauvegardez le fichier dans le dossier de destination
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # TODO: Ici, vous pourriez également uploader le fichier sur Supabase ou effectuer d'autres traitements
        
        return 'Image uploaded successfully', 200
    else:
        return 'Failed to upload image', 400
    

if __name__ == '__main__':
    app.run(debug=True)