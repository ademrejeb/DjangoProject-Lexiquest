# evaluation/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Reponse, Question
from .forms import ReponseForm
import google.generativeai as genai
from difflib import SequenceMatcher  # Pour la similarité

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
    questions = Question.objects.all()  # Récupérer toutes les questions
    return render(request, 'evaluation/accueil.html', {'questions': questions})

# Vue pour la liste des réponses
class ListeReponsesView(ListView):
    model = Reponse
    template_name = 'evaluation/liste_reponses.html'

# # Vue pour créer une réponse
# class CreerReponseView(CreateView):
#     model = Reponse
#     form_class = ReponseForm
#     template_name = 'evaluation/creer_reponse.html'
#     success_url = reverse_lazy('liste_reponses')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         question_id = self.kwargs.get('question_id')
#         context['question'] = get_object_or_404(Question, id=question_id)
#         return context

#     def form_valid(self, form):
#         question_id = self.kwargs.get('question_id')
#         question = get_object_or_404(Question, id=question_id)
#         form.instance.utilisateur = self.request.user
#         form.instance.question = question  # Associez la réponse à la question
#         return super().form_valid(form)

# Vue pour soumettre une réponse à une question avec correction automatique
# def soumettre_reponse(request, question_id):
#     question = get_object_or_404(Question, id=question_id)

#     if request.method == 'POST':
#         form = ReponseForm(request.POST)
        
#         if form.is_valid():
#             reponse_texte = form.cleaned_data['texte']
            
#             # Ajout du prompt contextuel basé sur la question
#             prompt = f"Given the question: '{question.texte}', evaluate if the answer provided: '{reponse_texte}' is correct. If incorrect, provide the correct answer."

#             # Envoi de la réponse à Gemini pour obtenir une correction basée sur la question
#             chat_session = model.start_chat(history=[])
#             gemini_response = chat_session.send_message(prompt)
#             generated_response = gemini_response.text.strip().lower()

#             # Comparaison améliorée : vérification si la réponse correcte est contenue dans la réponse de Gemini
#             correct_answer = question.reponse_correcte.strip().lower()
#             est_correct = correct_answer in generated_response
            
#             # Lignes de débogage
#             print(f"Réponse de Gemini : '{generated_response}'")
#             print(f"Réponse correcte attendue : '{correct_answer}'")
#             print(f"Est-ce correct ? : {est_correct}")
            
#             # Sauvegarde de la réponse dans la base de données
#             reponse_obj = Reponse(
#                 texte=reponse_texte,
#                 question=question,
#                 utilisateur=request.user,
#                 est_correct=est_correct
#             )
#             reponse_obj.save()

#             # Messages pour l'utilisateur
#             if est_correct:
#                 messages.success(request, "Correct ! Votre réponse est correcte.")
#             else:
#                 messages.error(request, f"Incorrect ! La réponse correcte est : {question.reponse_correcte}")

#             # Affichage de la réponse de Gemini
#             messages.info(request, f"Réponse de Gemini : {generated_response}")

#             # return redirect('liste_reponses')
#     else:
#         form = ReponseForm()

#     return render(request, 'evaluation/soumettre_reponse.html', {
#         'question': question,
#         'form': form
#     })


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def soumettre_reponse(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        form = ReponseForm(request.POST)
        
        if form.is_valid():
            reponse_texte = form.cleaned_data['texte']
            
            # Configure prompt for API request based on the question and response
            prompt = (
                f"Given the question: '{question.texte}' and the provided answer: '{reponse_texte}', "
                f"determine if the answer is correct or incorrect based on the correct answer: "
                f"'{question.reponse_correcte}'. Respond with 'correct' or 'incorrect' only."
            )

            # Interact with Gemini for evaluation
            chat_session = model.start_chat(history=[])
            gemini_response = chat_session.send_message(prompt)
            generated_response = gemini_response.text.strip().lower()

            # Determine correctness based on Gemini response
            est_correct = generated_response == "correct"
            
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
                messages.error(request, f"Incorrect! La réponse correcte est: {question.reponse_correcte}")

            messages.info(request, f"Réponse de Gemini: {generated_response}")
            return redirect('liste_reponses')
    else:
        form = ReponseForm()

    return render(request, 'evaluation/soumettre_reponse.html', {
        'question': question,
        'form': form
    })


# Vue pour modifier une réponse
class ModifierReponseView(UpdateView):
    model = Reponse
    form_class = ReponseForm
    template_name = 'evaluation/modifier_reponse.html'
    success_url = reverse_lazy('liste_reponses')

# Vue pour supprimer une réponse
class SupprimerReponseView(DeleteView):
    model = Reponse
    template_name = 'evaluation/supprimer_reponse.html'
    success_url = reverse_lazy('liste_reponses')
