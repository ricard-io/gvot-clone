from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from .base import views

urlpatterns = [
    # Wagtail's applications
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    # Local applications
    path('docs/', include('docs.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.views import defaults as default_views

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path('400/', default_views.bad_request,
             kwargs={'exception': Exception('Bad Request!')}),
        path('403/', default_views.permission_denied,
             kwargs={'exception': Exception('Permission Denied')}),
        path('404/', default_views.page_not_found,
             kwargs={'exception': Exception('Page not Found')}),
        path('500/', default_views.server_error),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))

# Root application
urlpatterns += [
    path('<uuid:uuid>/', views.RootUUID.as_view(), name='uuid'),
    path('', include(wagtail_urls)),
]
