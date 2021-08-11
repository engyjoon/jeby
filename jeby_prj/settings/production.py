from .base import *

DEBUG = False

STATIC_ROOT = BASE_DIR / 'static/'
STATICFILES_DIRS = []

INSTALLED_APPS.append('django_crontab')

# CRONJOBS = [
#     ('*/30 * * * *', 'news.cron.send_mail',
#      [], {}, '>> '+BASE_DIR+'/log/send_mail.log 2>&1'),
# ]
