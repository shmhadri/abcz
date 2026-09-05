from django.urls import path

from english_path import views

app_name = "english_path"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("review/", views.review, name="review"),
    path("review/start/", views.start_review_session, name="start_review_session"),
    path("review/<int:item_id>/answer/", views.review_answer, name="review_answer"),
    path("assessment/", views.assessment, name="assessment"),
    path("assessment/submit/", views.submit_assessment, name="submit_assessment"),
    path("a1/final-challenge/", views.a1_final_challenge, name="a1_final"),
    path("a1/final-challenge/submit/", views.submit_a1_final, name="submit_a1_final"),
    path("a2/final-challenge/", views.a2_final_challenge, name="a2_final"),
    path("a2/final-challenge/submit/", views.submit_a2_final, name="submit_a2_final"),
    path("completion/", views.journey_completion, name="journey_completion"),
    path("unit/<slug:unit_slug>/", views.unit_detail, name="unit"),
    path("unit/<slug:unit_slug>/progress/", views.save_unit_progress, name="save_progress"),
    path("unit/<slug:unit_slug>/quiz/", views.submit_unit_quiz, name="submit_unit_quiz"),
    path("unit/<slug:unit_slug>/quiz/similar/", views.check_similar_question, name="check_similar_question"),
    path("<slug:level_slug>/", views.level_detail, name="level"),
]
