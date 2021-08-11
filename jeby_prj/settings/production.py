from .base import *

DEBUG = False

STATIC_ROOT = BASE_DIR / 'static/'
STATICFILES_DIRS = []

INSTALLED_APPS.append('django_crontab')

CRONJOBS = [
    ('35 * * * *', 'news.cron.send_mail', '>> /tmp/djangocron.log'),
]
