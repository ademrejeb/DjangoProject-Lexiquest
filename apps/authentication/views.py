# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# authentication/views.py
import os 
from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from .forms import LoginForm, SignUpForm
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib import messages
import face_recognition
import numpy as np
from django.views.decorators.csrf import csrf_exempt
from .forms import UserProfileForm
from .utils import extract_text_from_cv, extract_keywords, get_coursera_courses
import google.generativeai as genai

def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')  # Use cleaned data from form
            password = form.cleaned_data.get('password')  # Use cleaned data from form
            print(f"Trying to log in with Username: {username}, Password: {password}")
            user = authenticate(request, username=username, password=password)  # Default Django authentication
            print(user)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                print("Authentication failed")  # Debugging line
                msg = 'Invalid credentials'
        else:
            print("Form is not valid")  # Debugging line
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})




def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")

            # Create the user instance without saving it yet
            user = form.save(commit=False)  # commit=False creates the user but doesn't save to the database yet

            # Set the password and hash it
            user.set_password(raw_password)
            user.save() 
            print(f"User created: {email}, Password: {raw_password}")  # Debugging line
           # user = authenticate(email=email, password=raw_password)  # Authenticate by email
            
            if user is not None:
                msg = 'User created - please <a href="/login">login</a>.'
                success = True
            else:
                msg = 'Authentication failed. Please try again.'
        else:
            msg = 'Form is not valid. Please correct the errors below.'
            print(form.errors)
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def users_list(request):
   
    users = CustomUser.objects.all()

    # Optionally, filter the users based on some criteria, e.g., only active users:
    # users = CustomUser.objects.filter(is_active=True)

    # Pass the users to the template context
    return render(request, "Admin/Userslist.html", {"users": users})




def delete_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return JsonResponse({'status': 'success'})
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return JsonResponse({'status': 'error', 'message': 'User not found.'})
    





def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        cv_file = request.FILES.get('cv_file')

        if form.is_valid():
            # Save the user profile form first
            form.save()  
            
            # If a CV file was uploaded, save it to the user instance
            if cv_file:
                user.cv_file = cv_file  # Assign the uploaded CV file
                user.save()  # Save the user again to update the CV file field
            
            # Now you can extract text from the uploaded CV file
            if user.cv_file:  # Check if cv_file exists
                file_path = user.cv_file.path  # Get the actual file path
                extracted_text = extract_text_from_cv(file_path)  # Extract text from CV
                keywords = extract_keywords(extracted_text)  # Extract keywords
                print("Extracted Keywords:", keywords)
                print(keywords['languages'])
                user.skills = keywords['skills'] if keywords['skills'] else ''
                user.education = keywords['education'] if keywords['education'] else ''
                user.languages = keywords['languages'] if keywords['languages'] else ''
                print(user.languages)
                user.save()


        else:
            print("Form errors:", form.errors)  # Print form errors for debugging
    else:
        form = UserProfileForm(instance=user)

    context = {
        'form': form,
        'user': user  
    }
    return render(request, 'home/profile.html', context)


from django.contrib.auth import get_backends
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login
import os
import face_recognition
from scipy.spatial.distance import euclidean

@csrf_exempt  # Use this carefully; ideally, add proper CSRF handling
def face_recognition_view(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        try:
            # Load the uploaded image and get face encodings
            image = face_recognition.load_image_file(image_file)
            face_encodings = face_recognition.face_encodings(image)

            if face_encodings:  # If faces are found in the uploaded image
                uploaded_encoding = face_encodings[0]  # Use the first face found

                # Iterate over known users and compare faces
                known_users = CustomUser.objects.all()
                for user in known_users:
                    if not user.image:  # Skip users without an image
                        print(f"User {user.email} has no associated image.")
                        continue
                    
                    known_image_path = user.image.path
                    print("User image path:", known_image_path)  # Debugging line

                    if os.path.exists(known_image_path):
                        # Load user's stored image and get its face encoding
                        known_image = face_recognition.load_image_file(known_image_path)
                        known_encodings = face_recognition.face_encodings(known_image)

                        if known_encodings:  # Check if face encoding exists for user's image
                            known_encoding = known_encodings[0]
                            # Calculate Euclidean distance between uploaded and known encoding
                            distance = euclidean(uploaded_encoding, known_encoding)
                            print(f"Euclidean distance for {user.email}: {distance}")  # Debugging line

                            tolerance_distance = 0.53
                            if distance <= tolerance_distance:
                                login(request, user)
                                return JsonResponse({'success': True, 'message': 'Face recognized and logged in!'})

                        else:
                            print(f"No faces found in the stored image for user: {user.email}")
                    else:
                        print(f"Image not found for user: {user.email}")  # Debugging line

                # If no matches are found
                return JsonResponse({'success': False, 'message': 'No matching face found.'})

            # If no faces are found in the uploaded image
            return JsonResponse({'success': False, 'message': 'No faces found in the image.'})

        except Exception as e:
            # Handle any other errors
            return JsonResponse({'success': False, 'message': f'Error processing image: {str(e)}'})

    # Handle GET request and render the HTML page
    return render(request, "accounts/face_recognition_sign_in.html")

def recommended_courses_view(request):
   
    
    # Retrieve the second item of education which contains skills
    education_details = request.user.education if request.user.education else None
   

    # Ensure you extract only the relevant skills portion
    if education_details:
        # Split by commas and take the first part before the newline
        skills_section = education_details.split('\n')[0]  # Get the first line with skills
        skills_to_search = [skill.strip() for skill in skills_section.split(',') if skill.strip()]  # Clean up whitespace
    else:
        skills_to_search = []

    all_courses = []
    
    # Loop through the cleaned skills and fetch courses
    for skill in skills_to_search:
        if skill:  # Ensure skill is not empty
            courses = get_coursera_courses(skill)  # Fetch courses using the cleaned skill
            all_courses.append({'skill': skill, 'courses': courses})
        
   
    return render(request, "home/courses.html", {
        "all_courses": all_courses
    })

genai.configure(api_key="AIzaSyAJJiqKKdd40c9Yu-zpojvnrut2dZN_6Yk")


def language_recommendation_view(request):
    user = request.user
    known_languages = user.languages.split(', ') if user.languages else []
    
    
    prompt = f"Given the languages {known_languages}, recommend a new spoken language to learn next in only one word which is the new language name , you should give me the best match related to the ones provided"
    
    try:
        # Generate the primary recommendation using Gemini API
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        language_name = response.text.strip()  # Store the recommended language name

        # Define follow-up prompts using the recommended language
        prompt2 = f"Given the languages {known_languages}, explain why I should learn {language_name} not a long paragraph and keep no things like *** or - ,"
        prompt3 = f"Recommend an easy way to learn {language_name} and provide tips , give me direclty bullet points and every bullet point should be in only line "

        # Generate reasoning and learning tips
        response2 = model.generate_content(prompt2)
        response3 = model.generate_content(prompt3)

        # Extract the reasoning and learning tips from the responses
        reasoning = response2.text.strip()
        learning_tips = response3.text.strip()
        
    except Exception as e:
        language_name = "Error"
        reasoning = "Error retrieving recommendation."
        learning_tips = "Please try again later."
        print(f"Error with Gemini API: {e}")
    
    return render(request, 'home/language_recommendation.html', {
        'language_name': language_name,
        'reasoning': reasoning,
        'learning_tips': learning_tips,
    })

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login/')  # Redirect to a page after logout
    else:
        # If it's a GET request, you might want to handle this differently
        return redirect('')