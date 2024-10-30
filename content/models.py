from django.db import models
import requests  
import os
import logging
import PyPDF2
import google.generativeai as genai


logger = logging.getLogger(__name__)

GEMINI_API_KEY='AIzaSyDVssqimNHpVW3Kc9s4eYwa4Kt60ZFRSmw'


genai.configure(api_key=GEMINI_API_KEY)  # En utilisant la clé API directement

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    language = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)  # Champ image ajouté
    file = models.FileField(upload_to='courses/')
    summary = models.TextField(null=True, blank=True)  # Nouveau champ pour stocker le résumé

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def extract_content_from_file(self, file_path, extension):
        """Extraire le contenu du fichier en fonction de son extension."""
        content = ""

        if extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

        elif extension == '.pdf':
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    content += page.extract_text()

        return content

    # def generate_questions_with_gemini(self, content):
    #     """Génère des questions et réponses à partir du contenu via l'API Gemini."""
    #     try:
    #         generation_config = {
    #             "temperature": 1,
    #             "top_p": 0.95,
    #             "top_k": 64,
    #             "max_output_tokens": 8192,
    #             "response_mime_type": "text/plain",
    #         }
    #         model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

    #         chat_session = model.start_chat(history=[])
    #         response = chat_session.send_message(content)

    #         # Retourne les réponses si elles sont présentes
    #         return response.text.split('\n') if response and response.text else None

    #     except Exception as e:
    #         logger.error(f"Gemini API Error: {e}")
    #         return None

    
    def generate_questions_with_gemini(self, content):
        """Génère des questions en format interrogatif à partir du contenu via l'API Gemini."""
        try:
            # Configuration pour générer des questions
            generation_config = {
                "temperature": 0.7,  # Une température plus basse pour des réponses plus précises
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 500,
                "response_mime_type": "text/plain",
            }
            model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

            # Ajout de l'instruction pour générer des questions
            prompt = f"Generate questions related to the following course content with the language of the content:\n\n{content}"

            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt)

            # Vérification et extraction des questions générées
            if response and response.text:
                questions = response.text.split('\n')
                # Filtrer pour obtenir uniquement les questions qui se terminent par un point d'interrogation
                questions = [q for q in questions if q.endswith('?')]
                return questions
            return None

        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return None

    
    def generate_answer_for_question(self, question_text):
        """Génère une réponse pour une question spécifique via l'API Gemini."""
        try:
            # Configuration pour la génération de réponses
            generation_config = {
                "temperature": 0.5,  # Réponse précise et concise
                "top_p": 0.9,
                "top_k": 50,
                "max_output_tokens": 300,
                "response_mime_type": "text/plain",
            }
            model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

            # Instruction pour obtenir une réponse
            prompt = f"Provide a detailed answer for the question: {question_text}"

            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt)

            # Renvoyer la réponse si disponible
            return response.text.strip() if response and response.text else None

        except Exception as e:
            logger.error(f"Gemini API Error while generating answer: {e}")
            return None


    def generate_summary(self, content):
        """Génère un résumé du contenu du cours via l'API Gemini."""
        try:
            generation_config = {
                "temperature": 0.5,
                "top_p": 0.9,
                "max_output_tokens": 300,
                "response_mime_type": "text/plain",
            }
            model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

            prompt = f"Summarize the following course content:\n\n{content}"

            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt)

            # Renvoyer le résumé si disponible
            return response.text.strip() if response and response.text else None

        except Exception as e:
            logger.error(f"Gemini API Error while generating summary: {e}")
            return None


    
    def process_file(self):
        """Analyse le fichier, génère des questions et des réponses pour le cours."""
        file_path = self.file.path
        extension = os.path.splitext(file_path)[1].lower()
        content = self.extract_content_from_file(file_path, extension)
        
        if content:
            # Générer le résumé et le stocker
            self.summary = self.generate_summary(content)
            self.save()  # Sauvegarder le résumé dans la base de données
            logger.info(f"Summary generated and saved: {self.summary}")


            questions = self.generate_questions_with_gemini(content)
            logger.info(f"Questions generated: {questions}")

            if questions:
                for question_text in questions:
                    # Créer chaque question dans la base de données
                    question = QuestionWithAnswer.objects.create(course=self, text=question_text)
                    
                    # Générer une réponse pour la question et la stocker
                    answer = self.generate_answer_for_question(question_text)
                    if answer:
                        question.answer = answer
                        question.save()
                    
            return {"summary": self.summary, "questions": questions}  # Retourne le résumé et les questions pour l'affichage
        return None


class QuestionWithAnswer(models.Model):
    course = models.ForeignKey(Course, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    answer = models.TextField(null=True, blank=True)  # Nouveau champ pour stocker les réponses


    def __str__(self):
        return self.text
