from django.db.models import Count

from rest_framework import generics, mixins, viewsets
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from funkwhale_api.music.models import Track
from funkwhale_api.common import permissions
from funkwhale_api.common import fields

from . import filters
from . import models
from . import serializers


class PlaylistViewSet(
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.PlaylistSerializer
    queryset = (
        models.Playlist.objects.all()
              .annotate(tracks_count=Count('playlist_tracks'))
    )
    permission_classes = [
        permissions.ConditionalAuthentication,
        permissions.OwnerPermission,
        IsAuthenticatedOrReadOnly,
    ]
    owner_checks = ['write']
    filter_class = filters.PlaylistFilter

    @detail_route(methods=['get'])
    def tracks(self, request, *args, **kwargs):
        playlist = self.get_object()
        plts = playlist.playlist_tracks.all()
        serializer = serializers.PlaylistTrackSerializer(plts, many=True)
        data = {
            'count': len(plts),
            'results': serializer.data
        }
        return Response(data, status=200)

    def get_queryset(self):
        return self.queryset.filter(
            fields.privacy_level_query(self.request.user))

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            privacy_level=serializer.validated_data.get(
                'privacy_level', self.request.user.privacy_level)
        )


class PlaylistTrackViewSet(
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.PlaylistTrackSerializer
    queryset = (models.PlaylistTrack.objects.all())
    permission_classes = [
        permissions.ConditionalAuthentication,
        permissions.OwnerPermission,
        IsAuthenticatedOrReadOnly,
    ]
    owner_field = 'playlist.user'
    owner_checks = ['write']

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE', 'POST']:
            return serializers.PlaylistTrackWriteSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.filter(
            fields.privacy_level_query(
                self.request.user,
                lookup_field='playlist__privacy_level'))

    def perform_destroy(self, instance):
        instance.delete(update_indexes=True)
