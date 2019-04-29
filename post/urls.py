from django.urls import path

from post import apis

urlpatterns = [
    path('api/write/', apis.write, name='post.api.write'),
    path('api/like/', apis.like, name='post.api.like'),
    path('api/unlike/', apis.unlike, name='post.api.unlike'),
    path('api/write/comment/', apis.write_comment, name='post.api.write_comment'),
    path('api/like/comment/', apis.like_comment, name='post.api.like_comment'),
    path('api/unlike/comment/', apis.unlike_comment, name='post.api.unlike_comment'),
    path('api/comments/', apis.get_comments, name='post.api.get_comments')
]
