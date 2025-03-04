from funkwhale_api.favorites import activities, serializers
from funkwhale_api.music.serializers import TrackActivitySerializer
from funkwhale_api.users.serializers import UserActivitySerializer


def test_get_favorite_activity_url(settings, factories):
    favorite = factories["favorites.TrackFavorite"]()
    user_url = favorite.user.get_activity_url()
    expected = f"{user_url}/favorites/tracks/{favorite.pk}"
    assert favorite.get_activity_url() == expected


def test_activity_favorite_serializer(factories):
    favorite = factories["favorites.TrackFavorite"]()

    actor = UserActivitySerializer(favorite.user).data
    field = serializers.serializers.DateTimeField()
    expected = {
        "type": "Like",
        "local_id": favorite.pk,
        "id": favorite.get_activity_url(),
        "actor": actor,
        "object": TrackActivitySerializer(favorite.track).data,
        "published": field.to_representation(favorite.creation_date),
    }

    data = serializers.TrackFavoriteActivitySerializer(favorite).data

    assert data == expected


def test_track_favorite_serializer_is_connected(activity_registry):
    conf = activity_registry["favorites.TrackFavorite"]
    assert conf["serializer"] == serializers.TrackFavoriteActivitySerializer


def test_track_favorite_serializer_instance_activity_consumer(activity_registry):
    conf = activity_registry["favorites.TrackFavorite"]
    consumer = activities.broadcast_track_favorite_to_instance_activity
    assert consumer in conf["consumers"]


def test_broadcast_track_favorite_to_instance_activity(factories, mocker):
    p = mocker.patch("funkwhale_api.common.channels.group_send")
    favorite = factories["favorites.TrackFavorite"]()
    data = serializers.TrackFavoriteActivitySerializer(favorite).data
    consumer = activities.broadcast_track_favorite_to_instance_activity
    message = {"type": "event.send", "text": "", "data": data}
    consumer(data=data, obj=favorite)
    p.assert_called_once_with("instance_activity", message)


def test_broadcast_track_favorite_to_instance_activity_private(factories, mocker):
    p = mocker.patch("funkwhale_api.common.channels.group_send")
    favorite = factories["favorites.TrackFavorite"](user__privacy_level="me")
    data = serializers.TrackFavoriteActivitySerializer(favorite).data
    consumer = activities.broadcast_track_favorite_to_instance_activity
    consumer(data=data, obj=favorite)
    p.assert_not_called()
