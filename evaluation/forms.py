# evaluation/forms.py

from django import forms
from .models import Reponse

class ReponseForm(forms.ModelForm):
    class Meta:
        model = Reponse
        fields = ['texte']
        widgets = {
            'texte': forms.Textarea(attrs={'placeholder': 'Votre réponse ici...', 'rows': 3}),
        }
from django import forms
