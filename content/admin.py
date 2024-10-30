from django.contrib import admin

from content.models import Course, QuestionWithAnswer

# Register your models here.
admin.site.register(Course)
admin.site.register(QuestionWithAnswer)