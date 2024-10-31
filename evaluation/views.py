# evaluation/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Reponse, Question
from .forms import ReponseForm
import google.generativeai as genai
from difflib import SequenceMatcher  # Pour la similarité
from content.models import QuestionWithAnswer
# Configurez l'API Gemini
GEMINI_API_KEY = 'AIzaSyDgETVHVtcsud7aoCaxhvob9ssITxU08l0'
genai.configure(api_key=GEMINI_API_KEY)

# Créer le modèle
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Vue pour la page d'accueil
def accueil(request):
    questions = QuestionWithAnswer.objects.all()
    return render(request, 'evaluation/accueil.html', {'questions': questions})

# Vue pour la liste des réponses
class ListeReponsesView(ListView):
    model = Reponse
    template_name = 'evaluation/liste_reponses.html'




from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def soumettre_reponse(request, question_id):
    question = get_object_or_404(QuestionWithAnswer, id=question_id)

    if request.method == 'POST':
        form = ReponseForm(request.POST)
        
        if form.is_valid():
            reponse_texte = form.cleaned_data['texte']
            
            # Configure prompt for API request based on the question and response
            prompt = (
                f"Given the question: '{question.text}' and the provided answer: '{reponse_texte}', "
                f"determine if the answer is correct or incorrect based on the correct answer: "
                f"'{question.answer}'. Respond with 'correct' or 'incorrect' only."
            )

            # Interact with Gemini for evaluation
            chat_session = model.start_chat(history=[])
            gemini_response = chat_session.send_message(prompt)
            generated_response = gemini_response.text.strip().lower()

            # Set a threshold for considering a response similar
            SIMILARITY_THRESHOLD = 0.8  # Adjust this as needed (0.8 is generally lenient)
            
            # Use difflib to calculate similarity ratio
            similarity_ratio = SequenceMatcher(None, reponse_texte.lower(), question.answer.lower()).ratio()
            est_correct = generated_response == "correct" or similarity_ratio >= SIMILARITY_THRESHOLD
            
            # Save the response with the logged-in user
            reponse_obj = Reponse(
                texte=reponse_texte,
                question=question,
                utilisateur=request.user,
                est_correct=est_correct
            )
            reponse_obj.save()

            # Provide feedback to the user
            if est_correct:
                messages.success(request, "Correct! Votre réponse est correcte.")
            else:
                messages.error(request, f"Incorrect! La réponse correcte est: {question.answer}")

            messages.info(request, f"Réponse de Gemini: {generated_response} | Similarity: {similarity_ratio:.2f}")
    else:
        form = ReponseForm()

    return render(request, 'evaluation/soumettre_reponse.html', {
        'question': question,
        'form': form
    })


class ModifierReponseView(UpdateView):
    model = Reponse
    form_class = ReponseForm
    template_name = 'evaluation/modifier_reponse.html'
    success_url = reverse_lazy('liste_reponses')

    def form_valid(self, form):
        # Retrieve updated response text
        reponse_texte = form.cleaned_data['texte']
        question = form.instance.question

        # Configure prompt for API request based on the question and response
        prompt = (
            f"Given the question: '{question.text}' and the provided answer: '{reponse_texte}', "
            f"determine if the answer is correct or incorrect based on the correct answer: "
            f"'{question.answer}'. Respond with 'correct' or 'incorrect' only."
        )

        # Interact with Gemini for evaluation
        chat_session = model.start_chat(history=[])
        gemini_response = chat_session.send_message(prompt)
        generated_response = gemini_response.text.strip().lower()

        # Set a threshold for considering a response similar
        SIMILARITY_THRESHOLD = 0.8  # Adjust as needed
        similarity_ratio = SequenceMatcher(None, reponse_texte.lower(), question.answer.lower()).ratio()
        est_correct = generated_response == "correct" or similarity_ratio >= SIMILARITY_THRESHOLD

        # Update the response with the evaluation result
        form.instance.est_correct = est_correct
        form.save()

        # Provide feedback to the user
        if est_correct:
            messages.success(self.request, "Correct! Votre réponse mise à jour est correcte.")
        else:
            messages.error(self.request, f"Incorrect! La réponse correcte est: {question.answer}")

        messages.info(self.request, f"Réponse de Gemini: {generated_response} | Similarity: {similarity_ratio:.2f}")
        
        return super().form_valid(form)

# Vue pour supprimer une réponse
class SupprimerReponseView(DeleteView):
    model = Reponse
    template_name = 'evaluation/supprimer_reponse.html'
    success_url = reverse_lazy('liste_reponses')
