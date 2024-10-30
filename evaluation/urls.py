# evaluation/urls.py
from django.urls import path
from . import views
from .views import ListeReponsesView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('acceuil/', views.accueil, name='accueil'),  # Page d'accueil
    path('reponses/', views.ListeReponsesView.as_view(), name='liste_reponses'),
    path('reponses/soumettre/<int:question_id>/', views.soumettre_reponse, name='soumettre_reponse'),  # Ajouter cette ligne
    #path('reponses/creer/<int:question_id>/', views.CreerReponseView.as_view(), name='creer_reponse'),  # URL pour créer une réponse
    path('reponses/<int:pk>/modifier/', views.ModifierReponseView.as_view(), name='modifier_reponse'),
    path('reponses/<int:pk>/supprimer/', views.SupprimerReponseView.as_view(), name='supprimer_reponse'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)