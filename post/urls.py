from django.urls import path

from post import apis

urlpatterns = [
    path('api/write/', apis.write, name='post.api.write'),
    path('api/like/', apis.like, name='post.api.like'),
    path('api/unlike/', apis.unlike, name='post.api.unlike')
]
