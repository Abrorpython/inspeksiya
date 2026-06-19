from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import FileResponse, Http404
from django.views.static import serve as static_serve
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
    # Serve uploaded media (logos, article/banner images, etc.).
    # NOTE: django.conf.urls.static.static() only wires this up when
    # DEBUG=True — on a real (DEBUG=False) production server it silently
    # adds nothing, so every uploaded file 404s. django.views.static.serve
    # works regardless of DEBUG. For higher traffic, it's better to have
    # nginx/Apache serve MEDIA_URL directly instead of Django, but this
    # guarantees uploads work out of the box on any deployment.
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    path('', serve_html('public/index.html')),
]