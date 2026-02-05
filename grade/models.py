from django.db import models
from django.contrib.auth.models import User, Group
from decimal import Decimal
from django.core.exceptions import PermissionDenied

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateField()
    weight = models.IntegerField(default=1)
    points = models.IntegerField(default=100)
    def __str__(self):
        return f"{self.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_assignments")
    grader = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="graded_set")
    file = models.FileField(null=True, blank=True)
    score = models.DecimalField(decimal_places=2, max_digits=100, blank=True, null=True)
    def __str__(self):
        return f"{self.assignment.title}"

    def change_grade(self, user: User, new_score):
        if self.grader != user:
            raise PermissionDenied("You're not allow to change this score.")
        
        self.score = new_score

    def view_submission(self, user):
        if user == self.author or user == self.grader or user.is_superuser:
            return self.file
        else:
            raise PermissionDenied("You're not allowed to access this file.")
