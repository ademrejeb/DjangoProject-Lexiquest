# evaluation/models.py

from django.db import models
from django.conf import settings  # Import settings to reference the custom user model

class Question(models.Model):
    texte = models.CharField(max_length=255, verbose_name="Texte de la question")
    reponse_correcte = models.CharField(max_length=255, verbose_name="Réponse correcte")

    def __str__(self):
        return self.texte

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"


class Reponse(models.Model):
    # Use settings.AUTH_USER_MODEL to reference the custom user model
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Utilisateur"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='reponses',
        verbose_name="Question"
    )
    texte = models.CharField(max_length=255, verbose_name="Texte de la réponse")
    est_correct = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    def __str__(self):
        return f"{self.utilisateur.username if self.utilisateur else 'Anonyme'} - {self.question.texte}"

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"