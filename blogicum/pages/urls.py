from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('pages/about/', views.AboutPage.as_view(), name='about'),
    path('pages/rules/', views.RulesPage.as_view(), name='rules'),
]
