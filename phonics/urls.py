from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/save-progress/', views.save_progress, name='save_progress'),
    path('api/speech/', views.speech_check, name='speech_check'),
    path('certificate/<int:student_id>/', views.generate_certificate, name='generate_certificate'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/letter-data/<str:letter>/', views.letter_data_api, name='letter_data_api'),
    path('cvc-reading/', views.cvc_reading_view, name='cvc_reading'),
    path('api/cvc-words/', views.get_cvc_words_api, name='api_get_cvc_words'),
    path('api/cvc-sentences/', views.get_cvc_sentences_api, name='api_get_cvc_sentences'),
    path('api/cvc-stories/', views.get_cvc_stories_api, name='api_get_cvc_stories'),
    path('api/save-cvc-progress/', views.save_cvc_progress_api, name='api_save_cvc_progress'),
    path('api/check-cvc-pronunciation/', views.check_cvc_pronunciation, name='api_check_cvc_pronunciation'),
]
