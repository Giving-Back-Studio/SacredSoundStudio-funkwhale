from django.conf.urls import include, url

from django_ses.views import SESEventWebhookView
from django.views.decorators.csrf import csrf_exempt

from funkwhale_api.activity import views as activity_views
from funkwhale_api.audio import views as audio_views
from funkwhale_api.common import routers as common_routers
from funkwhale_api.common import views as common_views
from funkwhale_api.music import views
from funkwhale_api.playlists import views as playlists_views
from funkwhale_api.tags import views as tags_views
from funkwhale_api.concerts import views as concerts_views

router = common_routers.OptionalSlashRouter()
router.register(r"activity", activity_views.ActivityViewSet, "activity")
router.register(r"tags", tags_views.TagViewSet, "tags")
router.register(r"tag-categories", tags_views.TagCategoryViewSet, "tag-categories")
router.register(r"plugins", common_views.PluginViewSet, "plugins")
router.register(r"tracks", views.TrackViewSet, "tracks")
router.register(r"uploads", views.UploadViewSet, "uploads")
router.register(r"libraries", views.LibraryViewSet, "libraries")
router.register(r"listen", views.ListenViewSet, "listen")
router.register(r"stream", views.StreamViewSet, "stream")
router.register(r"artists", views.ArtistViewSet, "artists")
router.register(r"channels", audio_views.ChannelViewSet, "channels")
router.register(r"subscriptions", audio_views.SubscriptionsViewSet, "subscriptions")
router.register(r"albums", views.AlbumViewSet, "albums")
router.register(r"licenses", views.LicenseViewSet, "licenses")
router.register(r"playlists", playlists_views.PlaylistViewSet, "playlists")
router.register(r"mutations", common_views.MutationViewSet, "mutations")
router.register(r"attachments", common_views.AttachmentViewSet, "attachments")
router.register(r"concerts", concerts_views.ConcertViewSet, "concerts")
v1_patterns = router.urls

v1_patterns += [
    url(r"^oembed/?$", views.OembedView.as_view(), name="oembed"),
    url(
        r"^instance/",
        include(("funkwhale_api.instance.urls", "instance"), namespace="instance"),
    ),
    url(
        r"^manage/",
        include(("funkwhale_api.manage.urls", "manage"), namespace="manage"),
    ),
    url(
        r"^moderation/",
        include(
            ("funkwhale_api.moderation.urls", "moderation"), namespace="moderation"
        ),
    ),
    url(
        r"^federation/",
        include(
            ("funkwhale_api.federation.api_urls", "federation"), namespace="federation"
        ),
    ),
    url(
        r"^providers/",
        include(("funkwhale_api.providers.urls", "providers"), namespace="providers"),
    ),
    url(
        r"^favorites/",
        include(("funkwhale_api.favorites.urls", "favorites"), namespace="favorites"),
    ),
    url(r"^search$", views.Search.as_view(), name="search"),
    url(
        r"^radios/",
        include(("funkwhale_api.radios.urls", "radios"), namespace="radios"),
    ),
    url(
        r"^history/",
        include(("funkwhale_api.history.urls", "history"), namespace="history"),
    ),
    url(
        r"^",
        include(("funkwhale_api.users.api_urls", "users"), namespace="users"),
    ),
    # XXX: remove if Funkwhale 1.1
    url(
        r"^users/",
        include(("funkwhale_api.users.api_urls", "users"), namespace="users-nested"),
    ),
    url(
        r"^oauth/",
        include(("funkwhale_api.users.oauth.urls", "oauth"), namespace="oauth"),
    ),
    url(r"^rate-limit/?$", common_views.RateLimitView.as_view(), name="rate-limit"),
    url(
        r"^text-preview/?$", common_views.TextPreviewView.as_view(), name="text-preview"
    ),
    url(r'^ses/event-webhook/$', csrf_exempt(SESEventWebhookView.as_view()), name='handle-ses-event-webhook')
]

urlpatterns = [url("", include((v1_patterns, "v1"), namespace="v1"))]
