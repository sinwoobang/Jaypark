"""jaypark URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url=settings.MAIN_REDIRECT_URL)),  # To redirect to the main feed
    path('<username>/', RedirectView.as_view(pattern_name='feed_user')),  # To redirect to a user's feed
    path('admin/', admin.site.urls),
    path('feed/', include('feed.urls')),
    path('accounts/', include('accounts.urls')),
    path('post/', include('post.urls')),
]
