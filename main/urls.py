from django.contrib import admin
from django.urls import path, include, re_path
from authentication.views import index
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from .views import health_check, serve_media_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assignment_api.urls')),
    path('accounts/', include('authentication.urls')),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("health/", health_check, name="health_check"),
    # Serve media files from Firebase Realtime Database
    re_path(r'^media/(?P<path>.*)$', serve_media_file, name='serve_media_file'),
]


