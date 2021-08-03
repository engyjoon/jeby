from django.urls import path
from django.contrib.auth import views as auth_views
from news import views

app_name = 'common'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(
        template_name='common/login.html'),  name='login'),
]
