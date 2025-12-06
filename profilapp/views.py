from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
import google.generativeai as genai
from pymongo import MongoClient
import os
from django.conf import settings
# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["SubstanceAi"]
collection = db["profile"]

# Configuration Gemini - Lecture depuis Django settings
API_KEY = None
gemini_model = None

try:
    # Lire la clé depuis les settings Django
    API_KEY = getattr(settings, 'GEMINI_API_KEY', None)
    
    # Si pas dans settings, essayer les variables d'environnement
    if not API_KEY:
        API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not API_KEY:
        #logger.error("❌ GEMINI_API_KEY non trouvée dans settings.py ni dans les variables d'environnement")
        raise Exception("Clé API Gemini manquante")
    
    # Configurer Gemini
    genai.configure(api_key=API_KEY)
    gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")
    
    # Test de fonctionnement
    test_response = gemini_model.generate_content("Test")
    #logger.info("✅ Gemini configuré et testé avec succès")
    #logger.info(f"✅ Clé API: {API_KEY[:10]}...")
    
except Exception as e:
    #logger.error(f"❌ Erreur configuration Gemini: {str(e)}")
    gemini_model = None


def generate_gemini_question(questions_reponses, is_first_question=False):
    if is_first_question:
        return "Pouvez-vous me dire quel est votre domaine d'intérêt principal ?"
    
    historique = []
    for qa in questions_reponses:
        if qa.get("reponse"):
            historique.append(f"Q: {qa['question']}")
            historique.append(f"R: {qa['reponse']}")
    historique_str = "\n".join(historique)
    prompt = """Tu es un assistant IA spécialisé dans la création de profils utilisateur personnalisés.
HISTORIQUE:
{}
MISSION: Génère une question courte, naturelle et pertinente pour cet utilisateur.
Réponds uniquement avec la question, sans explication.""".format(historique_str)

#     prompt = f"""Tu es un assistant IA spécialisé dans la création de profils utilisateur personnalisés.
# HISTORIQUE:
# {"\n".join(historique)}
# MISSION: Génère une question courte, naturelle et pertinente pour cet utilisateur.
# Réponds uniquement avec la question, sans explication."""
    
    response = gemini_model.generate_content(prompt)
    question = response.text.strip().replace('"', '').replace("'", "").replace("?", "") + " ?"
    return question


# ✅ Start profiling
@csrf_exempt
def start_profiling(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        max_questions = data.get("max_questions", 5)
        if not user_id:
            return JsonResponse({"error": "user_id manquant"}, status=400)

        first_question = generate_gemini_question([], is_first_question=True)
        questions_reponses = [{"question": first_question, "reponse": None, "created_at": datetime.now().isoformat()}]

        existing_profile = collection.find_one({"user_id": user_id})
        profile_data = {
            "user_id": user_id,
            "questions_reponses": questions_reponses,
            "updated_at": datetime.now().isoformat()
        }
        if existing_profile:
            collection.update_one({"_id": existing_profile["_id"]}, {"$set": profile_data})
        else:
            collection.insert_one(profile_data)

        return JsonResponse({
            "next_question": first_question,
            "questions_reponses": questions_reponses,
            "max_questions": max_questions
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ✅ Answer profiling
@csrf_exempt
def answer_profiling(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        reponse = data.get("reponse")
        questions_reponses = data.get("questions_reponses", [])
        max_questions = data.get("max_questions", 5)

        if not user_id or reponse is None:
            return JsonResponse({"error": "user_id et reponse requis"}, status=400)

        if questions_reponses:
            questions_reponses[-1]["reponse"] = reponse
            questions_reponses[-1]["answered_at"] = datetime.now().isoformat()
        else:
            return JsonResponse({"error": "Pas de question en cours"}, status=400)

        if len(questions_reponses) >= max_questions:
            profile_data = {
                "user_id": user_id,
                "questions_reponses": questions_reponses,
                "updated_at": datetime.now().isoformat()
            }
            existing_profile = collection.find_one({"user_id": user_id})
            if existing_profile:
                collection.update_one({"_id": existing_profile["_id"]}, {"$set": profile_data})
            else:
                collection.insert_one(profile_data)

            return JsonResponse({
                "next_question": None,
                "questions_reponses": questions_reponses,
                "message": "Profil terminé !"
            })
        
        next_question = generate_gemini_question(questions_reponses)
        questions_reponses.append({"question": next_question, "reponse": None, "created_at": datetime.now().isoformat()})

        existing_profile = collection.find_one({"user_id": user_id})
        profile_data = {
            "user_id": user_id,
            "questions_reponses": questions_reponses,
            "updated_at": datetime.now().isoformat()
        }
        if existing_profile:
            collection.update_one({"_id": existing_profile["_id"]}, {"$set": profile_data})
        else:
            collection.insert_one(profile_data)

        return JsonResponse({
            "next_question": next_question,
            "questions_reponses": questions_reponses
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
