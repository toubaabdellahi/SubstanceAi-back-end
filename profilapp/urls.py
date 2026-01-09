from django.urls import path
from .views import (
    start_profiling,
    answer_profiling,
    get_user_profile
  #  test_gemini
)

urlpatterns = [
    # Démarrer le profiling stateless
    path("start/", start_profiling, name="start_profiling"),

    # Envoyer une réponse et générer la prochaine question
    path("answer/", answer_profiling, name="answer_profiling"),

    # Récupérer le profil complet d'un utilisateur
    path('recuperer/<str:user_id>/', get_user_profile, name='get_user_profile'),  # ✅ Nouvelle route
     #path("recuperer_reponses/<str:user_id>/", recuperer_reponses, name="recuperer_reponses"),  # ← AJOUTER 
   
]
