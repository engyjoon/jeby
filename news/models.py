from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models.fields import CharField


class Keyword(models.Model):
    title = models.CharField(max_length=50, unique=True)
    content = models.CharField(max_length=100)
    order = models.IntegerField(
        validators=[MinValueValidator(1)],
        unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    shared = models.BooleanField(default=False)

    def __str__(self):
        return self.title
