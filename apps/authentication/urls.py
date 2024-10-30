# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_user, logout_view,users_list,delete_user,edit_profile,face_recognition_view, recommended_courses_view ,language_recommendation_view
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path('users/', users_list, name="Users"),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    path("logout/", logout_view, name="logout"),
    path('face_recognition_sign_in/', face_recognition_view, name="face_recognition_sign_in"),
    path('courses/' ,  recommended_courses_view ,  name="recommended_courses_view" ),
    path('language-recommendation/', language_recommendation_view, name='language_recommendation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)