from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse, Http404
import os


def serve_html(template_path):
    def view(request, *args, **kwargs):
        full = os.path.join(settings.BASE_DIR, 'frontend', template_path)
        if os.path.exists(full):
            return FileResponse(open(full, 'rb'), content_type='text/html')
        raise Http404
    return view


urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('admin-panel/', serve_html('admin/index.html')),
    path('', serve_html('public/index.html')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)