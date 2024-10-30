# evaluation/models.py

from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    texte = models.CharField(max_length=255, verbose_name="Texte de la question")
    reponse_correcte = models.CharField(max_length=255, verbose_name="Réponse correcte")

    def __str__(self):
        return self.texte

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"


class Reponse(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Champ utilisateur nullable
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reponses')  # Champ question obligatoire
    texte = models.CharField(max_length=255, verbose_name="Texte de la réponse")
    est_correct = models.BooleanField(default=False)  # Champ pour indiquer si la réponse est correcte
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    def __str__(self):
        return f"{self.utilisateur.username if self.utilisateur else 'Anonyme'} - {self.question.texte}"

    class Meta:
        ordering = ['-date_creation']  # Pour trier les réponses par date de création, du plus récent au plus ancien
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
