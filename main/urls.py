from django.contrib import admin
from django.urls import path, include
from authentication.views import index
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assignment_api.urls')),
    path('accounts/', include('authentication.urls')),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


