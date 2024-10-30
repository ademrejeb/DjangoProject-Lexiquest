import requests
from django.shortcuts import render
from django.http import JsonResponse

# Remplacez par votre token d'API
API_TOKEN = "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"

def home(request):
    return render(request, 'translator/traduction.html')

def translate(request):
    if request.method == 'POST':
        input_text = request.POST.get('input_text')
        source_lang = request.POST.get('source_lang')
        target_lang = request.POST.get('target_lang')

        # Construisez l'URL du modèle en fonction des langues sélectionnées
        model_name = f"opus-mt-{source_lang}-{target_lang}"
        model_url = f"https://api-inference.huggingface.co/models/Helsinki-NLP/{model_name}"

        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": input_text,
            "options": {
                "use_cache": False
            }
        }

        # Envoyer la requête POST au modèle de traduction
        response = requests.post(model_url, headers=headers, json=payload)

        # Vérifiez le statut de la réponse
        if response.status_code == 200:
            output = response.json()
            # Extraire le texte traduit de la sortie
            generated_text = output[0]['translation_text']  # Clé correcte pour la sortie de traduction
            return JsonResponse({'generated_text': generated_text})
        else:
            # Retourner la réponse d'erreur avec le code d'état et le message d'erreur
            return JsonResponse({'error': response.json()}, status=response.status_code)

    # Retourner une erreur pour les requêtes invalides
    return JsonResponse({'error': 'Invalid request'}, status=400)
