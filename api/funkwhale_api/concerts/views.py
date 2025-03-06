import mux_python
import os
from dotenv import load_dotenv
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Concert
from .serializers import ConcertSerializer

# Load environment variables
load_dotenv()

# Configure Mux API
configuration = mux_python.Configuration()
configuration.username = os.getenv("MUX_TOKEN_ID")
configuration.password = os.getenv("MUX_TOKEN_SECRET")
live_streams_api = mux_python.LiveStreamsApi(mux_python.ApiClient(configuration))

class ConcertViewSet(viewsets.ModelViewSet):
    queryset = Concert.objects.all()
    serializer_class = ConcertSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = ConcertSerializer(data=data)
        if serializer.is_valid():
            # Create Mux live stream
            create_live_stream_request = mux_python.CreateLiveStreamRequest(
                playback_policy=["public"],
                new_asset_settings={"playback_policy": ["public"]},
                reduced_latency=True
            )
            live_stream = live_streams_api.create_live_stream(create_live_stream_request)

            # Save Concert with Mux data
            concert = serializer.save(
                mux_live_stream_id=live_stream.id,
                mux_playback_id=live_stream.playback_ids[0].id
            )

            return Response(ConcertSerializer(concert).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
