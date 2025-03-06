from django.apps import AppConfig


class ConcertConfig(AppConfig):
    name = 'funkwhale_api.concerts'

    def ready(self):
        from . import signals