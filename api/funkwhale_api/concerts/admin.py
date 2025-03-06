from funkwhale_api.common import admin

from . import models


@admin.register(models.Concert)
class ConcertAdmin(admin.ModelAdmin):
    list_display = ["title", "start_time", "end_time"]
    search_fields = ["title", "description"]
    readonly_fields = ["mux_live_stream_id", "mux_playback_id"]