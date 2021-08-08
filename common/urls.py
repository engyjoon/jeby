from django.urls import path
from django.contrib.auth import views as auth_views
from news import views

app_name = 'common'

urlpatterns = [
    path('', views.news_search, name='search'),
    path('login/', auth_views.LoginView.as_view(
        template_name='common/login.html'),  name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
