import random
import json
from test_plus.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from model_mommy import mommy

from funkwhale_api.users.models import User
from funkwhale_api.history import models

class TestHistory(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='test', email='test@test.com', password='test')

    def test_can_create_listening(self):
        track = mommy.make('music.Track')
        now = timezone.now()
        l = models.Listening.objects.create(user=self.user, track=track)

    def test_anonymous_user_can_create_listening_via_api(self):
        track = mommy.make('music.Track')
        url = self.reverse('api:history:listenings-list')
        response = self.client.post(url, {
            'track': track.pk,
        })

        listening = models.Listening.objects.latest('id')

        self.assertEqual(listening.track, track)
        self.assertIsNotNone(listening.session_key)

    def test_logged_in_user_can_create_listening_via_api(self):
        track = mommy.make('music.Track')

        self.client.login(username=self.user.username, password='test')

        url = self.reverse('api:history:listenings-list')
        response = self.client.post(url, {
            'track': track.pk,
        })

        listening = models.Listening.objects.latest('id')

        self.assertEqual(listening.track, track)
        self.assertEqual(listening.user, self.user)
