from django.contrib import admin

from content.models import Course, Question

# Register your models here.
admin.site.register(Course)
admin.site.register(Question)