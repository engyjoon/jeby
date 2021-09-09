from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # path('', views.news_search, name='search'),
    path('search/', views.news_search, name='search'),
    path('keyword/', views.KeywordList.as_view(), name='keyword'),
    path('keyword/create/', views.KeywordCreate.as_view(), name='keyword_create'),
    path('keyword/update/<int:pk>/',
        views.KeywordUpdate.as_view(), name='keyword_update'),
    path('keyword/delete/<int:pk>/', views.keyword_delete, name='keyword_delete'),
    path('recipient/', views.RecipientList.as_view(), name='recipient'),
    path('recipient/create/', views.RecipientCreate.as_view(), name='recipient_create'),
    path('recipient/update/<int:pk>/',
        views.RecipientUpdate.as_view(), name='recipient_update'),
    path('recipient/delete/<int:pk>/', views.recipient_delete, name='recipient_delete'),
    path('email/', views.email_setting, name='email_setting'),
    path('site', views.SiteCreateGenericAPIView.as_view(), name='site_create'),
    path('site/<int:pk>',
        views.SiteUpdateGenericAPIView.as_view(), name='site_update'),
    path('share', views.share_news, name='share'),
]
