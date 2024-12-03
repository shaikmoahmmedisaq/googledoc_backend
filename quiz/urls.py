from .views import QuestionView, FormView, FormResponseView
from django.urls import path

urlpatterns = [
        path('questions/', QuestionView.as_view()),
        path('forms/<pk>/', FormView.as_view()),
        path('form-response/<pk>/', FormResponseView.as_view())
]
