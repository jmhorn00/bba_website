from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('contact/', include('contact.urls', namespace='contact')),
    path('pay/', include('payments.urls', namespace='payments')),
    path('financial-tools/calculators/', include('calculators.urls', namespace='calculators')),
    path('', include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
    except ImportError:
        pass
