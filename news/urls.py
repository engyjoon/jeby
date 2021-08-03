from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('search/', views.news_search, name='search')
]
