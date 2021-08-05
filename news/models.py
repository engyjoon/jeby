from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models.fields import CharField


class Keyword(models.Model):
    title = models.CharField(max_length=50, unique=True)
    content = models.CharField(max_length=100)
    mailing = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    order = models.IntegerField(
        validators=[MinValueValidator(1)],
        unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
