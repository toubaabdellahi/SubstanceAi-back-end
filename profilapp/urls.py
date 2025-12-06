from django.urls import path
from .views import (
    start_profiling,
    answer_profiling
  #  test_gemini
)

urlpatterns = [
    # Démarrer le profiling stateless
    path("start/", start_profiling, name="start_profiling"),

    # Envoyer une réponse et générer la prochaine question
    path("answer/", answer_profiling, name="answer_profiling"),

    # Récupérer le profil complet d'un utilisateur
   # path("recuperer_reponses/<str:user_id>/", recuperer_reponses, name="recuperer_reponses"),

    # Test et diagnostic de Gemini
   # path("test_gemini/", test_gemini, name="test_gemini"),
]
