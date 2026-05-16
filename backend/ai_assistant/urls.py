from django.urls import path

from .views import ai_categorize, ai_chat

urlpatterns = [
    path('ai/categorize/', ai_categorize, name='ai-categorize'),
    path('ai/chat/', ai_chat, name='ai-chat'),
]
