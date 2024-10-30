from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Question
import logging
from django.http import HttpResponse, FileResponse, Http404
import mimetypes
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO

logger = logging.getLogger(__name__)

# def course_list(request):
#     courses = Course.objects.all()
#     return render(request, 'content/course_list.html', {'courses': courses})
def course_list(request):
    language_filter = request.GET.get('language')  # Récupérer le filtre de langue depuis la requête
    courses = Course.objects.all()

    # Appliquer le filtre si une langue est sélectionnée
    if language_filter:
        courses = courses.filter(language=language_filter)

    # Récupérer toutes les langues distinctes pour le filtre
    languages = Course.objects.values_list('language', flat=True).distinct()

    return render(request, 'content/course_list.html', {
        'courses': courses,
        'languages': languages,  # Passer les langues au template
        'selected_language': language_filter  # Passer la langue sélectionnée
    })

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = course.questions.all()  # Récupère les questions associées

    return render(request, 'content/course_detail.html', {'course': course, 'questions': questions})



def add_course(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        language = request.POST.get('language')
        image = request.FILES.get('image')
        file = request.FILES.get('file')
        # Créer un nouvel objet Course
        course = Course(title=title, description=description, language=language,image=image, file=file)
        course.save()

        # Générer des questions
        questions = course.process_file()

        # Rediriger vers la page de détails du cours ou afficher les questions
        return render(request, 'content/course_detail.html', {'course': course, 'questions': questions})

    return render(request, 'content/add_course.html')



def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.title = request.POST['title']
        course.description = request.POST['description']
        course.save()
        return redirect('course_detail', course_id=course.id)
    return render(request, 'content/edit_course.html', {'course': course})

def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'content/delete_course.html', {'course': course})

def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        question.text = request.POST.get('text', question.text)
        question.save()
        return redirect('course_detail', course_id=question.course.id)
    return HttpResponse(status=405)

def edit_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        question.answer = request.POST.get('answer', question.answer)
        question.save()
        return redirect('course_detail', course_id=question.course.id)
    return HttpResponse(status=405)

def edit_summary(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.summary = request.POST.get('summary', course.summary)
        course.save()
        return redirect('course_detail', course_id=course.id)
    return HttpResponse(status=405)

def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        course_id = question.course.id
        question.delete()
        return redirect('course_detail', course_id=course_id)
    return HttpResponse(status=405)

def download_file(request, course_id):
    # Charger le cours et vérifier si le fichier existe
    course = get_object_or_404(Course, id=course_id)
    if not course.file:
        raise Http404("File does not exist")

    # Détecter le type MIME du fichier
    mime_type, _ = mimetypes.guess_type(course.file.path)

    # Créer une réponse de fichier
    response = FileResponse(open(course.file.path, 'rb'), content_type=mime_type)
    response['Content-Disposition'] = f'attachment; filename="{course.file.name}"'
    
    return response

def home(request):
    return render(request, 'content/home.html') 


def course_listFront(request):
    language_filter = request.GET.get('language')  # Récupérer le filtre de langue depuis la requête
    courses = Course.objects.all()

    # Appliquer le filtre si une langue est sélectionnée
    if language_filter:
        courses = courses.filter(language=language_filter)

    # Récupérer toutes les langues distinctes pour le filtre
    languages = Course.objects.values_list('language', flat=True).distinct()

    return render(request, 'content/frontoffice/courses_front.html', {
        'courses': courses
    })

def course_detailFront(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = course.questions.all()  # Récupère les questions associées

    return render(request, 'content/frontoffice/course_detail_front.html', {'course': course, 'questions': questions})

def download_summary(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    html = render_to_string('content/frontoffice/my_template.html', {'course': course})  # Pass only the course data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="summary.pdf"'
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response.write(result.getvalue())
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)
