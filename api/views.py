import os
import tempfile
import traceback
from pymongo import MongoClient
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from api.engine import SubstanciaEngineUniversal

# Configuration MongoDB
MONGO_URI = "mongodb+srv://Substance:Collegue1%402026%23Mongo@cluster0.deh4w.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["SubstanceAi"]
profiles_collection = db["profiles"]

class AskAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        pdf_paths = []
        try:
            question = request.data.get("message")
            user_id = request.data.get("user_id")
            uploaded_files = request.FILES.getlist('file')

            # 1. Récupération du profil
            user_data = profiles_collection.find_one({"user_id": user_id})
            
            raw_profile = []
            if user_data and "questions_reponses" in user_data:
                raw_profile = user_data["questions_reponses"]

            # 2. 🛡️ CONVERSION LISTE -> DICTIONNAIRE (Correction de l'erreur)
            # Si c'est une liste de type [{"question": "...", "reponse": "..."}, ...]
            user_profile_dict = {}
            if isinstance(raw_profile, list):
                for item in raw_profile:
                    # On extrait la question et la réponse pour créer le dictionnaire
                    q = item.get("question") or item.get("label")
                    r = item.get("reponse") or item.get("value")
                    if q and r:
                        user_profile_dict[q] = r
            elif isinstance(raw_profile, dict):
                user_profile_dict = raw_profile
            else:
                # Profil par défaut si rien n'est trouvé
                user_profile_dict = {
                    "Langue": "Français",
                    "Niveau": "Simple"
                }

            # 3. Gestion des fichiers temporaires
            temp_dir = tempfile.gettempdir()
            for f in uploaded_files:
                local_path = os.path.join(temp_dir, f.name)
                with open(local_path, 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                pdf_paths.append(local_path)

            # 4. Lancement de l'IA avec le dictionnaire nettoyé
            engine = SubstanciaEngineUniversal(user_profile_dict)
            if pdf_paths:
                engine.ingest_pdfs(pdf_paths)
            
            result = engine.ask(question)

            # 5. Nettoyage
            for p in pdf_paths:
                if os.path.exists(p):
                    os.remove(p)

            return Response({
                "answer": result.get("answer", ""),
                "sources": result.get("sources", [])
            })

        except Exception as e:
            traceback.print_exc()
            # Nettoyage de sécurité
            for p in pdf_paths:
                if os.path.exists(p): os.remove(p)
            return Response({"error": str(e)}, status=500)