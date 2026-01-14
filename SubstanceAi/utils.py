import gridfs
from pymongo import MongoClient

# Connexion à MongoDB
# MONGO_URI = "mongodb://localhost:27017/SubstanceAi"
# client = MongoClient(MONGO_URI)
# db = client.get_database()

MONGO_URI = "mongodb+srv://Substance:Collegue1%402026%23Mongo@cluster0.deh4w.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["SubstanceAi"]

users_collection = db["pdfs"]  # Collection MongoDB pour stocker les utilisateurs
fs = gridfs.GridFS(db)

import gridfs
from pymongo import MongoClient

# Connexion à MongoDB
MONGO_URI = "mongodb+srv://Substance:Collegue1%402026%23Mongo@cluster0.deh4w.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["SubstanceAi"]
fs = gridfs.GridFS(db)

def save_pdf_to_mongodb(file, user_id, message):
    """Sauvegarde un fichier PDF dans MongoDB GridFS avec l'ID utilisateur et le message (prompt)"""
    file_id = fs.put(
        file.read(),
        filename=file.name,
        user_id=user_id,
        message=message  # Ajout du message
    )
    return file_id

def list_user_pdfs(user_id):
    files = users_collection.find({"user_id": user_id})
    return [
        {
            "_id": str(file["_id"]),
            "filename": file.get("filename", "inconnu"),
            "length": file.get("length", 0)
        }
        for file in files
    ]


def get_pdf_from_mongodb(file_id):
    """Récupère un fichier PDF stocké dans MongoDB GridFS"""
    return fs.get(file_id)


import gridfs
from pymongo import MongoClient, DESCENDING

def get_pdf_content_from_mongodb(user_id):
    """
    Récupère et lit le contenu du dernier fichier PDF stocké via GridFS.
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client['SubstanceAi']
        fs = gridfs.GridFS(db)
        
        # 1. Trouver les métadonnées du dernier fichier de l'utilisateur
        # On cherche dans la collection 'fs.files' (gérée par GridFS)
        last_file_metadata = db['fs.files'].find_one(
            {"user_id": user_id}, # Assurez-vous d'avoir passé user_id lors du put()
            sort=[("uploadDate", DESCENDING)]
        )

        if not last_file_metadata:
            print("⚠️ Aucun fichier trouvé pour cet utilisateur dans GridFS")
            return None

        # 2. Récupérer le contenu binaire du fichier
        file_id = last_file_metadata['_id']
        grid_out = fs.get(file_id)
        pdf_binary_content = grid_out.read() # Ceci est du binaire (bytes)

        # 3. EXTRACTION DU TEXTE (Indispensable pour l'IA)
        # L'IA sur Render ne peut pas lire des bytes, elle veut du texte !
        import io
        import PyPDF2

        pdf_file = io.BytesIO(pdf_binary_content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        return full_text

    except Exception as e:
        print(f"❌ Erreur GridFS: {str(e)}")
        return None