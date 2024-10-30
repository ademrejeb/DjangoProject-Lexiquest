from django.contrib import admin
from .models import Question, Reponse

# Enregistrement des modèles dans l'interface d'administration
admin.site.register(Question)
admin.site.register(Reponse)
