from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include, path
from django.views import defaults as default_views

from config import plugins
from funkwhale_api.common import admin

plugins_patterns = plugins.trigger_filter(plugins.URLS, [], enabled=True)

api_patterns = [
    url("v1/", include("config.urls.api")),
    url("v2/", include("config.urls.api_v2")),
    url("subsonic/", include("config.urls.subsonic")),
]


urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    url(r"^api/", include((api_patterns, "api"), namespace="api")),
    url(
        r"^",
        include(
            ("funkwhale_api.federation.urls", "federation"), namespace="federation"
        ),
    ),
    url(r"^api/v1/auth/", include("funkwhale_api.users.rest_auth_urls")),
    url(r"^accounts/", include("allauth.urls")),
] + plugins_patterns

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r"^400/$", default_views.bad_request),
        url(r"^403/$", default_views.permission_denied),
        url(r"^404/$", default_views.page_not_found),
        url(r"^500/$", default_views.server_error),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("api/__debug__/", include(debug_toolbar.urls))
        ] + urlpatterns

    if "silk" in settings.INSTALLED_APPS:
        urlpatterns = [
            url(r"^api/silk/", include("silk.urls", namespace="silk"))
        ] + urlpatterns
