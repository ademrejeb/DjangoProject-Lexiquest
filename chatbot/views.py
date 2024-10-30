import os
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
import google.generativeai as genai

genai.configure(api_key="AIzaSyAJJiqKKdd40c9Yu-zpojvnrut2dZN_6Yk")
# Vue pour rendre la page HTML du chatbot
def chatbot_view(request):
    return render(request, "chatbot/chatbot.html")
class ChatbotAPI(View):
    def post(self, request):
        user_input = request.POST.get("message", "")
        
        if not user_input:
            return JsonResponse({"error": "Message is required."}, status=400)

        try:
            # Définir la configuration du modèle
            generation_config = {
                "temperature": 0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                system_instruction="You are an AI language learning assistant created to help users learn new languages interactively. ...",  # Gardez le texte comme dans votre exemple
            )

            # Démarrer la session de chat et obtenir la réponse
            chat_session = model.start_chat(
                history=[{"role": "user", "parts": [user_input]}]
            )
            response = chat_session.send_message(user_input)

            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
