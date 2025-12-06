from rest_framework import serializers
from .models import ProfilingTest

class ProfilingTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilingTest
        fields = ["user_id", "questions_reponses", "score_completion"]
