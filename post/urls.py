from django.urls import path

from post import apis

urlpatterns = [
    path('api/write/', apis.write)
]
