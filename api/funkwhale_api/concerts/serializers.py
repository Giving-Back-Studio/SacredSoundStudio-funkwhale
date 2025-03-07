from rest_framework import serializers

from funkwhale_api.music.serializers import SimpleArtistSerializer

from .models import Concert

class ConcertSerializer(serializers.ModelSerializer):

    artist = SimpleArtistSerializer()

    class Meta:
        model = Concert
        fields = '__all__'
