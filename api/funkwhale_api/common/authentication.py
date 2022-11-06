from django.utils.translation import ugettext as _

from django.core.cache import cache

from allauth.account.utils import send_email_confirmation
from oauth2_provider.contrib.rest_framework.authentication import (
    OAuth2Authentication as BaseOAuth2Authentication,
)
from rest_framework import exceptions

from funkwhale_api.users import models as users_models


class UnverifiedEmail(Exception):
    def __init__(self, user):
        self.user = user


def resend_confirmation_email(request, user):
    THROTTLE_DELAY = 500
    cache_key = "auth:resent-email-confirmation:{}".format(user.pk)
    if cache.get(cache_key):
        return False

    done = send_email_confirmation(request, user)
    cache.set(cache_key, True, THROTTLE_DELAY)
    return done


class OAuth2Authentication(BaseOAuth2Authentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except UnverifiedEmail as e:
            request.oauth2_error = {"error": "unverified_email"}
            resend_confirmation_email(request, e.user)


class ApplicationTokenAuthentication(object):
    def authenticate(self, request):
        try:
            header = request.headers["Authorization"]
        except KeyError:
            return

        if "Bearer" not in header:
            return

        token = header.split()[-1].strip()

        try:
            application = users_models.Application.objects.exclude(user=None).get(
                token=token
            )
        except users_models.Application.DoesNotExist:
            return
        user = users_models.User.objects.all().for_auth().get(id=application.user_id)
        if not user.is_active:
            msg = _("User account is disabled.")
            raise exceptions.AuthenticationFailed(msg)

        if user.should_verify_email():
            raise UnverifiedEmail(user)

        request.scopes = application.scope.split()
        return user, None
