from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models.fields import CharField


class Keyword(models.Model):
    title = models.CharField(max_length=50, verbose_name='관리명')
    content = models.CharField(max_length=100, verbose_name='키워드')
    mailing = models.BooleanField(default=False, verbose_name='메일발송')
    shared = models.BooleanField(default=False, verbose_name='공유')
    order = models.IntegerField(
        validators=[MinValueValidator(1)],
        unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
        unique_together = ('title', 'author',)
