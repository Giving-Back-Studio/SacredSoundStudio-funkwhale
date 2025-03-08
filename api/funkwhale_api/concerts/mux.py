import os

import mux_python

MUX_TOKEN_ID = os.getenv("MUX_TOKEN_ID")
MUX_TOKEN_SECRET = os.getenv("MUX_TOKEN_SECRET")


def get_mux_live_stream_client():
    if not MUX_TOKEN_ID or not MUX_TOKEN_SECRET:
        return None

    configuration = mux_python.Configuration()
    configuration.username = MUX_TOKEN_ID
    configuration.password = MUX_TOKEN_SECRET
    return mux_python.LiveStreamsApi(mux_python.ApiClient(configuration))


def create_mux_stream(concert):
    live_streams_api = get_mux_live_stream_client()

    if not live_streams_api:
        return

    # Create Mux live stream
    create_live_stream_request = mux_python.CreateLiveStreamRequest(
        playback_policy=["public"],
        new_asset_settings={"playback_policy": ["public"]},
        reduced_latency=True
    )
    live_stream = live_streams_api.create_live_stream(create_live_stream_request)

    return live_stream