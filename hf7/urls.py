"""hf7 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from sesame.views import LoginView

from utilities.views import EmailLoginView, landing, logout_user

urlpatterns = [
    path("admin/", admin.site.urls),
    path("eventium/", include("eventium.urls")),
    path("sesame/login/", LoginView.as_view(), name="sesame-login"),
    path("tasks/", include("tasks.urls")),
    path("login/", EmailLoginView.as_view(), name="email-login"),
    path("logout/", logout_user, name="logout"),
    path("profile/", include("utilities.urls")),
    path("", landing, name="landing"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
