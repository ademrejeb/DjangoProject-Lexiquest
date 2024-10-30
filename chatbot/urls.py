from django.urls import path
from .views import chatbot_view, ChatbotAPI

urlpatterns = [
    path("", chatbot_view, name="chatbot_view"),  # Rendre la page HTML
    path("api/", ChatbotAPI.as_view(), name="chatbot_api"),  # API pour interagir avec le chatbot
]