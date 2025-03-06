from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Concert
from .mux import create_mux_stream


@receiver(pre_save, sender=Concert)
def handle_mux_stream(sender, instance, **kwargs):
    if not instance.mux_live_stream_id:
        live_stream = create_mux_stream(instance)
        if live_stream:
            instance.mux_live_stream_id = live_stream.data.stream_key
            instance.mux_playback_id = live_stream.data.playback_ids[0].id