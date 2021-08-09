from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models.fields import CharField


class Keyword(models.Model):
    title = models.CharField(max_length=50, verbose_name='관리명', unique=False)
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
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique title for author')
        ]


class Setting(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    email_send_time = CharField(
        max_length=100, verbose_name='메일발송시간', null=True, blank=True)
    email_recipient = CharField(
        max_length=200, verbose_name='메일수신자', null=True, blank=True)
