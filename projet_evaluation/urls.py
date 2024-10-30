"""
URL configuration for projet_evaluation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# projet_evaluation/urls.py

from django.contrib import admin
from django.urls import path, include
from evaluation import views  # Importer la vue d'accueil

urlpatterns = [
    path('admin/', admin.site.urls),
    path('evaluation/', include('evaluation.urls')),  # Inclure les routes de l'application evaluation
    path('', views.accueil, name='accueil'),  # Page d'accueil
]

