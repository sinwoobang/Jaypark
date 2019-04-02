from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.urls import urlpatterns as default_urlpatterns

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html')),
]
urlpatterns += default_urlpatterns  # Default Django supported views of accounts

