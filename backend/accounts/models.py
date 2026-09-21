from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    target_exam = models.CharField(max_length=50, blank=True, null=True, default='JEE Advanced')
    target_year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.username or self.email
