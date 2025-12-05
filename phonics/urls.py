from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/save-progress/', views.save_progress, name='save_progress'),
    path('api/speech/', views.speech_check, name='speech_check'),
    path('certificate/<int:student_id>/', views.generate_certificate, name='generate_certificate'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]