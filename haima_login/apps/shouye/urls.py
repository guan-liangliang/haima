from django.urls import path
from apps.shouye import views

urlpatterns = [
    path('', views.Home_Index.as_view()),
]