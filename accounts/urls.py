from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.urls import urlpatterns as default_urlpatterns

from accounts import views, apis

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html')),
    path('register/', views.register, name='account.register'),
]

urlpatterns += [
    path('follow/', apis.follow, name='account.api.follow'),
]
urlpatterns += default_urlpatterns  # Default Django supported views of accounts

