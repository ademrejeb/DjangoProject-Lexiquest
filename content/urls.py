from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # La route pour la page d'accueil
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),  # Détails d'un cours
    path('courses/add/', views.add_course, name='add_course'),  # Ajout d'un cours
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),  # Modification d'un cours
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),  # Suppression d'un cours
    path('courses/edit_question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('courses/edit_answer/<int:question_id>/', views.edit_answer, name='edit_answer'),
    path('course/<int:course_id>/edit_summary/', views.edit_summary, name='edit_summary'),
    path('courses/delete_question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('courses/<int:course_id>/download/', views.download_file, name='download_file'),


    path('coursesFront/', views.course_listFront, name='course_listFront'),
    path('coursesFront/<int:course_id>/', views.course_detailFront, name='course_detailFront'),

    path('download_summary/<int:course_id>/', views.download_summary, name='download_summary'),



]
