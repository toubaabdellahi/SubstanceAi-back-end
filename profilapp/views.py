from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
from pymongo import MongoClient
import random

# # Connexion MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client["SubstanceAi"]
MONGO_URI = "mongodb+srv://Substance:Collegue1%402026%23Mongo@cluster0.deh4w.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["SubstanceAi"]

collection = db["profile"]

# ✅ Questions structurées avec choix multiples
ALL_QUESTIONS = [
    # Langue & Communication (4 questions)
    {
        "id": 1,
        "category": "Langue & Communication",
        "question": "Quelle langue préfères-tu pour apprendre ?",
        "type": "single",
        "options": ["Français", "Anglais"]
    },
    {
        "id": 2,
        "category": "Langue & Communication",
        "question": "Quel niveau de langue préfères-tu dans les explications ?",
        "type": "single",
        "options": ["Simple et accessible", "Technique et précis", "Mixte selon le sujet"]
    },
    {
        "id": 3,
        "category": "Langue & Communication",
        "question": "Acceptes-tu le mélange des langues (code-switching) ?",
        "type": "single",
        "options": ["Oui, ça m'aide à comprendre", "Non, je préfère une seule langue", "Peu importe"]
    },
    {
        "id": 4,
        "category": "Langue & Communication",
        "question": "Préfères-tu un ton :",
        "type": "single",
        "options": ["Formel et académique", "Amical et décontracté", "Motivant et encourageant"]
    },

    # Profil académique (2 questions)
    {
        "id": 5,
        "category": "Profil académique",
        "question": "Quel est ton niveau d'études actuel ?",
        "type": "single",
        "options": ["Primaire", "Secondaire", "Licence", "Master", "Doctorat", "Autodidacte"]
    },
    {
        "id": 6,
        "category": "Profil académique",
        "question": "As-tu déjà suivi des formations en ligne ?",
        "type": "single",
        "options": ["Jamais", "Occasionnellement", "Souvent"]
    },

    # Objectifs d'apprentissage (3 questions)
    {
        "id": 7,
        "category": "Objectifs d'apprentissage",
        "question": "Pourquoi veux-tu apprendre ?",
        "type": "single",
        "options": ["Réussir un examen", "Trouver un emploi", "Améliorer mes compétences", "Changer de carrière",
                    "Par passion"]
    },
    {
        "id": 8,
        "category": "Objectifs d'apprentissage",
        "question": "Quel est ton objectif principal ?",
        "type": "single",
        "options": ["Acquérir des bases solides", "Devenir opérationnel rapidement", "Devenir expert",
                    "Résoudre des problèmes concrets", "Créer des projets réels"]
    },
    {
        "id": 9,
        "category": "Objectifs d'apprentissage",
        "question": "Souhaites-tu obtenir :",
        "type": "single",
        "options": ["Un certificat", "Des compétences pratiques", "Les deux"]
    },

    # Domaine & niveau (2 questions)
    {
        "id": 10,
        "category": "Domaine & niveau",
        "question": "Quel domaine veux-tu apprendre ?",
        "type": "single",
        "options": ["Informatique / Programmation", "Data / Intelligence Artificielle", "Mathématiques",
                    "Business / Entrepreneuriat", "Langues", "Autre"]
    },
    {
        "id": 11,
        "category": "Domaine & niveau",
        "question": "As-tu déjà des bases dans ce domaine ?",
        "type": "single",
        "options": ["Aucune", "Débutant", "Intermédiaire", "Avancé"]
    },

    # Style d'apprentissage (5 questions)
    {
        "id": 12,
        "category": "Style d'apprentissage",
        "question": "Préfères-tu :",
        "type": "single",
        "options": ["Des explications courtes", "Des explications détaillées"]
    },
    {
        "id": 13,
        "category": "Style d'apprentissage",
        "question": "Aimes-tu apprendre par :",
        "type": "multiple",
        "options": ["Exercices", "Projets", "Quiz"]
    },
    {
        "id": 14,
        "category": "Style d'apprentissage",
        "question": "Préfères-tu apprendre :",
        "type": "single",
        "options": ["Seul", "Accompagné (coach, groupe, IA)"]
    },
    {
        "id": 15,
        "category": "Style d'apprentissage",
        "question": "Apprends-tu mieux avec des schémas / images ?",
        "type": "single",
        "options": ["Oui", "Non"]
    },
    {
        "id": 16,
        "category": "Style d'apprentissage",
        "question": "Préfères-tu une approche :",
        "type": "single",
        "options": ["Théorique d'abord", "Pratique d'abord"]
    },

    # Temps & rythme (3 questions)
    {
        "id": 17,
        "category": "Temps & rythme",
        "question": "Combien d'heures par semaine peux-tu consacrer à l'apprentissage ?",
        "type": "single",
        "options": ["Moins de 2 heures", "2 – 5 heures", "5 – 10 heures", "Plus de 10 heures"]
    },
    {
        "id": 18,
        "category": "Temps & rythme",
        "question": "À quels moments apprends-tu le mieux ?",
        "type": "multiple",
        "options": ["Matin", "Après-midi", "Soir", "Nuit"]
    },
    {
        "id": 19,
        "category": "Temps & rythme",
        "question": "Es-tu :",
        "type": "single",
        "options": ["Régulier", "Irrégulier"]
    },

    # Motivation & comportement (2 questions)
    {
        "id": 20,
        "category": "Motivation & comportement",
        "question": "Comment réagis-tu à l'échec ?",
        "type": "single",
        "options": ["Je recommence et j'essaie encore", "Je perds motivation"]
    },
    {
        "id": 21,
        "category": "Motivation & comportement",
        "question": "Aimes-tu les défis difficiles ?",
        "type": "single",
        "options": ["Oui", "Non"]
    },

    # Technologie & accès (3 questions)
    {
        "id": 22,
        "category": "Technologie & accès",
        "question": "Quel appareil utilises-tu le plus ?",
        "type": "single",
        "options": ["Smartphone", "PC", "Tablette"]
    },
    {
        "id": 23,
        "category": "Technologie & accès",
        "question": "As-tu une bonne connexion Internet ?",
        "type": "single",
        "options": ["Oui", "Moyenne", "Non"]
    },
    {
        "id": 24,
        "category": "Technologie & accès",
        "question": "Préfères-tu du contenu :",
        "type": "single",
        "options": ["En ligne", "Téléchargeable"]
    }
]

# Questions fixes (toujours posées)
FIXED_QUESTION_IDS = [1, 5, 7, 10, 17]  # 5 questions fixes

# Questions aléatoires (pool)
RANDOM_QUESTION_IDS = [2, 3, 4, 6, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24]


def get_question_by_id(question_id):
    """Récupère une question par son ID"""
    for q in ALL_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def generate_questions_for_user(user_id, num_random=5):
    """Génère la liste des questions pour un utilisateur"""
    random.seed(user_id)

    # Sélectionner des questions aléatoires
    selected_random_ids = random.sample(RANDOM_QUESTION_IDS, min(num_random, len(RANDOM_QUESTION_IDS)))

    random.seed()

    # Combiner : questions fixes + questions aléatoires
    all_question_ids = FIXED_QUESTION_IDS + selected_random_ids

    # Récupérer les questions complètes
    questions = [get_question_by_id(qid) for qid in all_question_ids]

    return questions


# ✅ Start profiling
@csrf_exempt
def start_profiling(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        num_random = data.get("num_random_questions", 5)

        if not user_id:
            return JsonResponse({"error": "user_id manquant"}, status=400)

        # Générer les questions pour cet utilisateur
        user_questions = generate_questions_for_user(user_id, num_random)

        # Première question
        first_question = user_questions[0]
        questions_reponses = [{
            "question_id": first_question["id"],
            "category": first_question["category"],
            "question": first_question["question"],
            "type": first_question["type"],
            "options": first_question["options"],
            "reponse": None,
            "is_fixed": first_question["id"] in FIXED_QUESTION_IDS,
            "created_at": datetime.now().isoformat()
        }]

        existing_profile = collection.find_one({"user_id": user_id})
        profile_data = {
            "user_id": user_id,
            "questions_reponses": questions_reponses,
            "user_questions": user_questions,
            "num_fixed_questions": len(FIXED_QUESTION_IDS),
            "num_random_questions": num_random,
            "updated_at": datetime.now().isoformat()
        }

        if existing_profile:
            collection.update_one({"_id": existing_profile["_id"]}, {"$set": profile_data})
        else:
            collection.insert_one(profile_data)

        return JsonResponse({
            "next_question": {
                "question_id": first_question["id"],
                "category": first_question["category"],
                "question": first_question["question"],
                "type": first_question["type"],
                "options": first_question["options"]
            },
            "questions_reponses": questions_reponses,
            "max_questions": len(user_questions),
            "num_fixed_questions": len(FIXED_QUESTION_IDS),
            "num_random_questions": num_random,
            "question_type": "fixed" if first_question["id"] in FIXED_QUESTION_IDS else "random"
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

        if not user_id or reponse is None:
            return JsonResponse({"error": "user_id et reponse requis"}, status=400)

        if not questions_reponses:
            return JsonResponse({"error": "Pas de question en cours"}, status=400)

        # Enregistrer la réponse
        questions_reponses[-1]["reponse"] = reponse
        questions_reponses[-1]["answered_at"] = datetime.now().isoformat()

        # Récupérer le profil existant
        existing_profile = collection.find_one({"user_id": user_id})
        if not existing_profile:
            return JsonResponse({"error": "Profil non trouvé"}, status=404)

        user_questions = existing_profile.get("user_questions", [])

        # Vérifier si on a atteint toutes les questions
        if len(questions_reponses) >= len(user_questions):
            profile_data = {
                "user_id": user_id,
                "questions_reponses": questions_reponses,
                "user_questions": user_questions,
                "updated_at": datetime.now().isoformat()
            }
            collection.update_one({"_id": existing_profile["_id"]}, {"$set": profile_data})

            return JsonResponse({
                "next_question": None,
                "questions_reponses": questions_reponses,
                "message": "Profil terminé ! Merci d'avoir répondu à toutes les questions."
            })

        # Obtenir la prochaine question
        next_question_index = len(questions_reponses)
        next_question = user_questions[next_question_index]
        is_fixed = next_question["id"] in FIXED_QUESTION_IDS

        questions_reponses.append({
            "question_id": next_question["id"],
            "category": next_question["category"],
            "question": next_question["question"],
            "type": next_question["type"],
            "options": next_question["options"],
            "reponse": None,
            "is_fixed": is_fixed,
            "created_at": datetime.now().isoformat()
        })

        # Sauvegarder dans MongoDB
        profile_data = {
            "user_id": user_id,
            "questions_reponses": questions_reponses,
            "user_questions": user_questions,
            "updated_at": datetime.now().isoformat()
        }
        collection.update_one({"_id": existing_profile["_id"]}, {"$set": profile_data})

        return JsonResponse({
            "next_question": {
                "question_id": next_question["id"],
                "category": next_question["category"],
                "question": next_question["question"],
                "type": next_question["type"],
                "options": next_question["options"]
            },
            "questions_reponses": questions_reponses,
            "remaining_questions": len(user_questions) - len(questions_reponses),
            "question_type": "fixed" if is_fixed else "random"
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ Récupérer le profil d'un utilisateur
@csrf_exempt
def get_user_profile(request, user_id):
    if request.method != "GET":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        profile = collection.find_one({"user_id": user_id})

        if not profile:
            return JsonResponse({"error": "Profil non trouvé"}, status=404)

        profile['_id'] = str(profile['_id'])

        user_questions = profile.get('user_questions', [])
        questions_reponses = profile.get('questions_reponses', [])

        is_complete = len(questions_reponses) >= len(user_questions) and \
                      all(q.get('reponse') for q in questions_reponses)

        return JsonResponse({
            "user_id": profile['user_id'],
            "questions_reponses": questions_reponses,
            "total_questions": len(user_questions),
            "answered_questions": len([q for q in questions_reponses if q.get('reponse')]),
            "is_complete": is_complete,
            "updated_at": profile.get('updated_at')
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)