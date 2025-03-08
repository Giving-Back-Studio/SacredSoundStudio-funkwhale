from django.db import models

class Concert(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover = models.ImageField(upload_to="concert_covers/")

    artist = models.ForeignKey('music.Artist', on_delete=models.CASCADE, blank=True, null=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    mux_live_stream_id = models.CharField(max_length=100, blank=True, null=True)
    mux_playback_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
