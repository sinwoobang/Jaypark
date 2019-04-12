from django.urls import path

from feed import views

urlpatterns = (
    path('', views.feed),
    path('<username>/', views.feed_user, name='feed_user'),
)
