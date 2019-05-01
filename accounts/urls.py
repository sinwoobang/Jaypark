from django.urls import path
from django.contrib.auth.urls import urlpatterns as default_urlpatterns

from accounts import views, apis

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='account.login'),
    path('register/', views.register, name='account.register'),
]

urlpatterns += [
    path('api/login/', apis.login, name='account.api.login'),
    path('api/register/', apis.register, name='account.api.register'),
    path('api/follow/', apis.follow, name='account.api.follow'),
    path('api/unfollow/', apis.unfollow, name='account.api.unfollow'),
    path('api/update/', apis.update, name='account.api.update'),
]
urlpatterns += default_urlpatterns  # Default Django supported views of accounts

