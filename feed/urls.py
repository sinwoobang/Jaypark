from django.urls import path

from feed import views

urlpatterns = (
    path('', views.feed, name='feed.index'),
    path('search/', views.feed_search, name='feed.search'),
    path('<username>/', views.feed_user, name='feed.user'),
)
