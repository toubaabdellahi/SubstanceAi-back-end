from django.db import models

class ProfilingTest(models.Model):
    """
    Ce modèle sert uniquement de référence/documentation pour Djongo.
    Les données sont stockées dans MongoDB (via pymongo dans views.py).
    """
    user_id = models.CharField(max_length=255)
    questions_reponses = models.JSONField(default=list)  # Liste des Q/R
    score_completion = models.IntegerField(default=0)

    def __str__(self):
        return f"Profil de {self.user_id} ({self.score_completion}%)"
