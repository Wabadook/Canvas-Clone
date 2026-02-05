from django.contrib import admin
from .models import Assignment
from .models import Submission

class AdminAssignment(admin.ModelAdmin):
    list_display=['id', 'title', 'deadline', 'weight', 'points']
    ordering=['id']

class AdminSubmission(admin.ModelAdmin):
    list_display=['id', 'assignment_title', 'author', 'grader']
    ordering=['id']
    
    #Display the title of the assignment instead of object(id).
    def assignment_title(self, obj):
        return obj.assignment.title


admin.site.register(Assignment, AdminAssignment)
admin.site.register(Submission, AdminSubmission)

