import logging.config
import sys
import warnings
from collections import OrderedDict
from urllib.parse import urlsplit

import environ
from celery.schedules import crontab

logger = logging.getLogger("funkwhale_api.config")
ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path("funkwhale_api")

env = environ.Env()
ENV = env
# If DEBUG is `true`, we automatically set the loglevel to "DEBUG"
# If DEBUG is `false`, we try to read the level from LOGLEVEL environment and default to "INFO"
LOGLEVEL = (
    "DEBUG" if env.bool("DEBUG", False) else env("LOGLEVEL", default="info").upper()
)
"""
Default logging level for the Funkwhale processes.

.. note::
    The `DEBUG` variable overrides the `LOGLEVEL` if it is set to `TRUE`.

    The `LOGLEVEL` value only applies if `DEBUG` is `false` or not present.

Available levels:

- ``debug``
- ``info``
- ``warning``
- ``error``
- ``critical``

"""

IS_DOCKER_SETUP = env.bool("IS_DOCKER_SETUP", False)


if env("FUNKWHALE_SENTRY_DSN", default=None) is not None:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    from funkwhale_api import __version__ as version

    sentry_sdk.init(
        dsn=env("FUNKWHALE_SENTRY_DSN"),
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=env("FUNKWHALE_SENTRY_SR", default=0.25),
        send_default_pii=False,
        environment="api",
        debug=env.bool("DEBUG", False),
        release=version,
    )
    sentry_sdk.set_tag("instance", env("FUNKWHALE_HOSTNAME"))

LOGGING_CONFIG = None
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"}
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "console"},
        },
        "loggers": {
            "funkwhale_api": {
                "level": LOGLEVEL,
                "handlers": ["console"],
                # required to avoid double logging with root logger
                "propagate": False,
            },
            "plugins": {
                "level": LOGLEVEL,
                "handlers": ["console"],
                # required to avoid double logging with root logger
                "propagate": False,
            },
            "": {"level": "WARNING", "handlers": ["console"]},
        },
    }
)

ENV_FILE = env_file = env("ENV_FILE", default=None)
"""
Path to a .env file to load
"""
if env_file:
    logger.info("Loading specified env file at %s", env_file)
    # we have an explicitly specified env file
    # so we try to load and it fail loudly if it does not exist
    env.read_env(env_file)
else:
    # we try to load from .env and config/.env
    # but do not crash if those files don't exist
    paths = [
        # /srv/funwhale/api/.env
        ROOT_DIR,
        # /srv/funwhale/config/.env
        ((ROOT_DIR - 1) + "config"),
    ]
    for path in paths:
        try:
            env_path = path.file(".env")
        except FileNotFoundError:
            logger.debug("No env file found at %s/.env", path)
            continue
        env.read_env(env_path)
        logger.info("Loaded env file at %s/.env", path)
        break

FUNKWHALE_PLUGINS_PATH = env(
    "FUNKWHALE_PLUGINS_PATH", default="/srv/funkwhale/plugins/"
)
"""
Path to a directory containing Funkwhale plugins.
These are imported at runtime.
"""
sys.path.append(FUNKWHALE_PLUGINS_PATH)
CORE_PLUGINS = [
    "funkwhale_api.contrib.scrobbler",
    "funkwhale_api.contrib.listenbrainz",
    "funkwhale_api.contrib.maloja",
]

LOAD_CORE_PLUGINS = env.bool("FUNKWHALE_LOAD_CORE_PLUGINS", default=True)
PLUGINS = [p for p in env.list("FUNKWHALE_PLUGINS", default=[]) if p]
"""
List of Funkwhale plugins to load.
"""
if LOAD_CORE_PLUGINS:
    PLUGINS = CORE_PLUGINS + PLUGINS

# Remove duplicates
PLUGINS = list(OrderedDict.fromkeys(PLUGINS))

if PLUGINS:
    logger.info("Running with the following plugins enabled: %s", ", ".join(PLUGINS))
else:
    logger.info("Running with no plugins")

from .. import plugins  # noqa

plugins.startup.autodiscover([p + ".funkwhale_startup" for p in PLUGINS])
DEPENDENCIES = plugins.trigger_filter(plugins.PLUGINS_DEPENDENCIES, [], enabled=True)
plugins.install_dependencies(DEPENDENCIES)
FUNKWHALE_HOSTNAME = None
FUNKWHALE_HOSTNAME_SUFFIX = env("FUNKWHALE_HOSTNAME_SUFFIX", default=None)
FUNKWHALE_HOSTNAME_PREFIX = env("FUNKWHALE_HOSTNAME_PREFIX", default=None)
if FUNKWHALE_HOSTNAME_PREFIX and FUNKWHALE_HOSTNAME_SUFFIX:
    # We're in traefik case, in development
    FUNKWHALE_HOSTNAME = "{}.{}".format(
        FUNKWHALE_HOSTNAME_PREFIX, FUNKWHALE_HOSTNAME_SUFFIX
    )
    FUNKWHALE_PROTOCOL = env("FUNKWHALE_PROTOCOL", default="https")
else:
    try:
        FUNKWHALE_HOSTNAME = env("FUNKWHALE_HOSTNAME")
        """
        Hostname of your Funkwhale pod, e.g. ``mypod.audio``.
        """

        FUNKWHALE_PROTOCOL = env("FUNKWHALE_PROTOCOL", default="https")
        """
        Protocol end users will use to access your pod, either
        ``http`` or ``https``.
        """
    except Exception:
        FUNKWHALE_URL = env("FUNKWHALE_URL")
        _parsed = urlsplit(FUNKWHALE_URL)
        FUNKWHALE_HOSTNAME = _parsed.netloc
        FUNKWHALE_PROTOCOL = _parsed.scheme

FUNKWHALE_PROTOCOL = FUNKWHALE_PROTOCOL.lower()
FUNKWHALE_HOSTNAME = FUNKWHALE_HOSTNAME.lower()
FUNKWHALE_URL = f"{FUNKWHALE_PROTOCOL}://{FUNKWHALE_HOSTNAME}"
FUNKWHALE_SPA_HTML_ROOT = env("FUNKWHALE_SPA_HTML_ROOT", default=FUNKWHALE_URL)
"""
URL or path to the Web Application files.
Funkwhale needs access to it so that it can inject <meta> tags relevant
to the given page (e.g page title, cover, etc.).

If a URL is specified, the index.html file will be fetched through HTTP.
If a path is provided,
it will be accessed from disk.

Use something like ``/srv/funkwhale/front/dist/`` if the web processes shows
request errors related to this.
"""

FUNKWHALE_SPA_HTML_CACHE_DURATION = env.int(
    "FUNKWHALE_SPA_HTML_CACHE_DURATION", default=60 * 15
)
FUNKWHALE_EMBED_URL = env("FUNKWHALE_EMBED_URL", default=FUNKWHALE_URL + "/embed.html")
FUNKWHALE_SPA_REWRITE_MANIFEST = env.bool(
    "FUNKWHALE_SPA_REWRITE_MANIFEST", default=True
)
FUNKWHALE_SPA_REWRITE_MANIFEST_URL = env.bool(
    "FUNKWHALE_SPA_REWRITE_MANIFEST_URL", default=None
)

APP_NAME = "Funkwhale"

FEDERATION_HOSTNAME = env("FEDERATION_HOSTNAME", default=FUNKWHALE_HOSTNAME).lower()
FEDERATION_SERVICE_ACTOR_USERNAME = env(
    "FEDERATION_SERVICE_ACTOR_USERNAME", default="service"
)
# How many pages to fetch when crawling outboxes and third-party collections
FEDERATION_COLLECTION_MAX_PAGES = env.int("FEDERATION_COLLECTION_MAX_PAGES", default=5)
"""
Number of existing pages of content to fetch when discovering/refreshing an
actor or channel.

More pages means more content will be loaded, but will require more resources.
"""

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[]) + [FUNKWHALE_HOSTNAME]
"""
List of allowed hostnames for which the Funkwhale server will answer.
"""

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    "channels",
    "daphne",
    # Default Django apps:
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Useful template tags:
    # 'django.contrib.humanize',
    # Admin
    "django.contrib.admin",
)
THIRD_PARTY_APPS = (
    # 'crispy_forms',  # Form layouts
    "admin_sort",
    "allauth",  # registration
    "allauth.account",  # registration
    "allauth.socialaccount",  # registration"
    "corsheaders",
    "oauth2_provider",
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "dynamic_preferences",
    "django_filters",
    "django_cleanup",
    "versatileimagefield",
)


# Apps specific for this project go here.
LOCAL_APPS = (
    "funkwhale_api.common.apps.CommonConfig",
    "funkwhale_api.activity.apps.ActivityConfig",
    "funkwhale_api.users",  # custom users app
    "funkwhale_api.users.oauth",
    # Your stuff: custom apps go here
    "funkwhale_api.instance",
    "funkwhale_api.audio",
    "funkwhale_api.music",
    "funkwhale_api.requests",
    "funkwhale_api.favorites",
    "funkwhale_api.federation",
    "funkwhale_api.moderation.apps.ModerationConfig",
    "funkwhale_api.radios",
    "funkwhale_api.history",
    "funkwhale_api.playlists",
    "funkwhale_api.subsonic",
    "funkwhale_api.tags",
    "funkwhale_api.typesense",
    "funkwhale_api.concerts",
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps

ADDITIONAL_APPS = env.list("ADDITIONAL_APPS", default=[])
"""
List of Django apps to load in addition to Funkwhale plugins and apps.
"""
INSTALLED_APPS = (
    LOCAL_APPS
    + DJANGO_APPS
    + THIRD_PARTY_APPS
    + tuple(ADDITIONAL_APPS)
    + tuple(plugins.trigger_filter(plugins.PLUGINS_APPS, [], enabled=True))
)

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
ADDITIONAL_MIDDLEWARES_BEFORE = env.list("ADDITIONAL_MIDDLEWARES_BEFORE", default=[])
MIDDLEWARE = (
    tuple(plugins.trigger_filter(plugins.MIDDLEWARES_BEFORE, [], enabled=True))
    + tuple(ADDITIONAL_MIDDLEWARES_BEFORE)
    + (
        "django.middleware.security.SecurityMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        # needs to be before SPA middleware
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        # /end
        "funkwhale_api.common.middleware.SPAFallbackMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "funkwhale_api.users.middleware.RecordActivityMiddleware",
        "funkwhale_api.common.middleware.ThrottleStatusMiddleware",
    )
    + tuple(plugins.trigger_filter(plugins.MIDDLEWARES_AFTER, [], enabled=True))
)

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DJANGO_DEBUG = DEBUG = env.bool("DJANGO_DEBUG", False)
"""
Whether to enable debugging info and pages.
Never enable this on a production server, as it can leak very sensitive
information.
"""
# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------

# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default=f"Funkwhale <noreply@{FUNKWHALE_HOSTNAME}>"
)
"""
The name and email address used to send system emails.
Defaults to ``Funkwhale <noreply@yourdomain>``.

Available formats:

- ``Name <email address>``
- ``<Email address>``

"""
EMAIL_SUBJECT_PREFIX = env("EMAIL_SUBJECT_PREFIX", default="[Funkwhale] ")
"""
Subject prefix for system emails.
"""
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)


EMAIL_CONFIG = env.email_url("EMAIL_CONFIG", default="consolemail://")
"""
SMTP configuration for sending emails. Possible values:

- ``EMAIL_CONFIG=consolemail://``: output emails to console (the default)
- ``EMAIL_CONFIG=dummymail://``: disable email sending completely

On a production instance, you'll usually want to use an external SMTP server:

- ``EMAIL_CONFIG=smtp://user:password@youremail.host:25``
- ``EMAIL_CONFIG=smtp+ssl://user:password@youremail.host:465``
- ``EMAIL_CONFIG=smtp+tls://user:password@youremail.host:587``

"""
vars().update(EMAIL_CONFIG)

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases

# The `_database_url_docker` variable will only by used as default for DATABASE_URL
# in the context of a docker deployment.
_database_url_docker = None
if IS_DOCKER_SETUP and env.str("DATABASE_URL", None) is None:
    warnings.warn(
        DeprecationWarning(
            "the automatically generated 'DATABASE_URL' configuration in the docker "
            "setup is deprecated, please configure either the 'DATABASE_URL' "
            "environment variable or the 'DATABASE_HOST', 'DATABASE_USER' and "
            "'DATABASE_PASSWORD' environment variables instead"
        )
    )
    _DOCKER_DATABASE_HOST = "postgres"
    _DOCKER_DATABASE_PORT = 5432
    _DOCKER_DATABASE_USER = env.str("POSTGRES_ENV_POSTGRES_USER", "postgres")
    _DOCKER_DATABASE_PASSWORD = env.str("POSTGRES_ENV_POSTGRES_PASSWORD", "")
    _DOCKER_DATABASE_NAME = _DOCKER_DATABASE_USER

    _database_url_docker = (
        f"postgres:"
        f"//{_DOCKER_DATABASE_USER}:{_DOCKER_DATABASE_PASSWORD}"
        f"@{_DOCKER_DATABASE_HOST}:{_DOCKER_DATABASE_PORT}"
        f"/{_DOCKER_DATABASE_NAME}"
    )

DATABASE_HOST = env.str("DATABASE_HOST", "localhost")
"""
The hostname of the PostgreSQL server. Defaults to ``localhost``.
"""
DATABASE_PORT = env.int("DATABASE_PORT", 5432)
"""
The port of the PostgreSQL server. Defaults to ``5432``.
"""
DATABASE_USER = env.str("DATABASE_USER", "funkwhale")
"""
The name of the PostgreSQL user. Defaults to ``funkwhale``.
"""
DATABASE_PASSWORD = env.str("DATABASE_PASSWORD", "funkwhale")
"""
The password of the PostgreSQL user. Defaults to ``funkwhale``.
"""
DATABASE_NAME = env.str("DATABASE_NAME", "funkwhale")
"""
The name of the PostgreSQL database. Defaults to ``funkwhale``.
"""
DATABASE_URL = env.db(
    "DATABASE_URL",
    _database_url_docker  # This is only set in the context of a docker deployment.
    or (
        f"postgres:"
        f"//{DATABASE_USER}:{DATABASE_PASSWORD}"
        f"@{DATABASE_HOST}:{DATABASE_PORT}"
        f"/{DATABASE_NAME}"
    ),
)
"""
The URL used to connect to the PostgreSQL database. Defaults to an auto generated url
build using the `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`
and `DATABASE_NAME` variables.

Examples:
- ``postgresql://funkwhale@:5432/funkwhale``
- ``postgresql://<user>:<password>@<host>:<port>/<database>``
- ``postgresql://funkwhale:passw0rd@localhost:5432/funkwhale_database``
"""

DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
    "default": DATABASE_URL
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DB_CONN_MAX_AGE = DATABASES["default"]["CONN_MAX_AGE"] = env(
    "DB_CONN_MAX_AGE", default=60 * 5
)
"""
The maximum time in seconds before database connections close.
"""
MIGRATION_MODULES = {
    # see https://github.com/jazzband/django-oauth-toolkit/issues/634
    # swappable models are badly designed in oauth2_provider
    # ignore migrations and provide our own models.
    "oauth2_provider": None,
    "sites": "funkwhale_api.contrib.sites.migrations",
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
# see https://docs.djangoproject.com/en/4.0/releases/3.2/

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "UTC"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See:
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # See:
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            # See:
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": DEBUG,
            # See:
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # See:
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # Your stuff: custom template context processors go here
            ],
        },
    }
]

# See:
# http://django-crispy-forms.readthedocs.org/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap3"

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = env("STATIC_ROOT", default=str(ROOT_DIR("staticfiles")))
"""
The path where static files are collected.
"""
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = env("STATIC_URL", default=FUNKWHALE_URL + "/staticfiles/")
DEFAULT_FILE_STORAGE = "funkwhale_api.common.storage.ASCIIFileSystemStorage"

PROXY_MEDIA = env.bool("PROXY_MEDIA", default=True)
"""
Whether to proxy audio files through your reverse proxy.
We recommend you leave this enabled to enforce access control.

If you're using S3 storage with :attr:`AWS_QUERYSTRING_AUTH`
enabled, it's safe to disable this setting.
"""
AWS_DEFAULT_ACL = env("AWS_DEFAULT_ACL", default=None)
"""
The default ACL to use when uploading files to an S3-compatible object storage
bucket.

ACLs and bucket policies are distinct concepts, and some storage
providers (ie Linode, Scaleway) will always apply the most restrictive between
a bucket's ACL and policy, meaning a default private ACL will supersede
a relaxed bucket policy.

If present, the value should be a valid canned ACL.
See `<https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl>`_
"""
AWS_QUERYSTRING_AUTH = env.bool("AWS_QUERYSTRING_AUTH", default=not PROXY_MEDIA)
"""
Whether to include signatures in S3 URLs. Signatures
are used to enforce access control.

Defaults to the opposite of :attr:`PROXY_MEDIA`.
"""

AWS_S3_MAX_MEMORY_SIZE = env.int(
    "AWS_S3_MAX_MEMORY_SIZE", default=1000 * 1000 * 1000 * 20
)

AWS_QUERYSTRING_EXPIRE = env.int("AWS_QUERYSTRING_EXPIRE", default=3600)
"""
The time in seconds before AWS signatures expire.
Only takes effect you enable :attr:`AWS_QUERYSTRING_AUTH`
"""

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default=None)
"""
Access-key ID for your S3 storage.
"""

if AWS_ACCESS_KEY_ID:
    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    """
    Secret access key for your S3 storage.
    """
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    """
    Your S3 bucket name.
    """
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default=None)
    """
    Custom domain to use for your S3 storage.
    """
    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)
    """
    If you use a S3-compatible storage such as minio,
    set the following variable to the full URL to the storage server.

    Examples:

    - ``https://minio.mydomain.com``
    - ``https://s3.wasabisys.com``
    """
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default=None)
    """
    If you're using Amazon S3 to serve media without a proxy,
    you need to specify your region name to access files.

    Example:

    - ``eu-west-2``
    """

    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_LOCATION = env("AWS_LOCATION", default="")
    """
    A directory in your S3 bucket where you store files.
    Use this if you plan to share the bucket between services.
    """
    DEFAULT_FILE_STORAGE = "funkwhale_api.common.storage.ASCIIS3Boto3Storage"


# See:
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (str(APPS_DIR.path("static")),)

# See:
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = env("MEDIA_ROOT", default=str(APPS_DIR("media")))
"""
The path where you store media files (such as album covers or audio tracks)
on your system. Make sure this directory actually exists.
"""
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = env("MEDIA_URL", default=FUNKWHALE_URL + "/media/")
"""
The URL from which your pod serves media files. Change this if you're hosting media
files on a separate domain, or if you host Funkwhale on a non-standard port.
"""
FILE_UPLOAD_PERMISSIONS = 0o644

ATTACHMENTS_UNATTACHED_PRUNE_DELAY = env.int(
    "ATTACHMENTS_UNATTACHED_PRUNE_DELAY", default=3600 * 24
)
"""
The delay in seconds before Funkwhale prunes uploaded but detached attachments
from the system.
"""

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
SPA_URLCONF = "config.urls.spa"
ASGI_APPLICATION = "config.routing.application"

# This ensures that Django will be able to detect a secure connection
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    "funkwhale_api.users.auth_backends.ModelBackend",
    "funkwhale_api.users.auth_backends.AllAuthBackend",
)
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=3600 * 25 * 60)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION_ENFORCE = env.bool(
    "ACCOUNT_EMAIL_VERIFICATION_ENFORCE", default=False
)
"""
Set whether users need to verify their email address before using your pod. Enabling this setting
is useful for reducing spam and bot accounts. To use this setting you need to configure a mail server
to send verification emails. See :attr:`EMAIL_CONFIG`.

.. note::
    Superusers created through the command line never need to verify their email address.
"""
ACCOUNT_EMAIL_VERIFICATION = (
    "mandatory" if ACCOUNT_EMAIL_VERIFICATION_ENFORCE else "optional"
)
ACCOUNT_USERNAME_VALIDATORS = "funkwhale_api.users.serializers.username_validators"

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "users:redirect"
LOGIN_URL = "account_login"

# OAuth configuration
from funkwhale_api.users.oauth import scopes  # noqa

OAUTH2_PROVIDER = {
    "SCOPES": {s.id: s.label for s in scopes.SCOPES_BY_ID.values()},
    "ALLOWED_REDIRECT_URI_SCHEMES": ["http", "https", "urn"],
    # we keep expired tokens for 15 days, for tracability
    "REFRESH_TOKEN_EXPIRE_SECONDS": 3600 * 24 * 15,
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 5 * 60,
    "ACCESS_TOKEN_EXPIRE_SECONDS": env.int(
        "ACCESS_TOKEN_EXPIRE_SECONDS", default=60 * 60 * 10
    ),
    "OAUTH2_SERVER_CLASS": "funkwhale_api.users.oauth.server.OAuth2Server",
    "PKCE_REQUIRED": False,
}
OAUTH2_PROVIDER_APPLICATION_MODEL = "users.Application"
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = "users.AccessToken"
OAUTH2_PROVIDER_GRANT_MODEL = "users.Grant"
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = "users.RefreshToken"
OAUTH2_PROVIDER_ID_TOKEN_MODEL = "users.IdToken"

SCOPED_TOKENS_MAX_AGE = 60 * 60 * 24 * 3

# LDAP AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTH_LDAP_ENABLED = env.bool("LDAP_ENABLED", default=False)
"""
Whether to enable LDAP authentication.

See :doc:`/administrator_documentation/configuration_docs/ldap` for more information.
"""

if AUTH_LDAP_ENABLED:
    # Import the LDAP modules here.
    # This way, we don't need the dependency unless someone
    # actually enables the LDAP support
    import ldap
    from django_auth_ldap.config import GroupOfNamesType, LDAPSearch, LDAPSearchUnion

    # Add LDAP to the authentication backends
    AUTHENTICATION_BACKENDS += ("django_auth_ldap.backend.LDAPBackend",)

    # Basic configuration
    AUTH_LDAP_SERVER_URI = env("LDAP_SERVER_URI")
    AUTH_LDAP_BIND_DN = env("LDAP_BIND_DN", default="")
    AUTH_LDAP_BIND_PASSWORD = env("LDAP_BIND_PASSWORD", default="")
    AUTH_LDAP_SEARCH_FILTER = env("LDAP_SEARCH_FILTER", default="(uid={0})").format(
        "%(user)s"
    )
    AUTH_LDAP_START_TLS = env.bool("LDAP_START_TLS", default=False)
    AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = env(
        "AUTH_LDAP_BIND_AS_AUTHENTICATING_USER", default=False
    )

    DEFAULT_USER_ATTR_MAP = [
        "first_name:givenName",
        "last_name:sn",
        "username:cn",
        "email:mail",
    ]
    LDAP_USER_ATTR_MAP = env.list("LDAP_USER_ATTR_MAP", default=DEFAULT_USER_ATTR_MAP)
    AUTH_LDAP_USER_ATTR_MAP = {}
    for m in LDAP_USER_ATTR_MAP:
        funkwhale_field, ldap_field = m.split(":")
        AUTH_LDAP_USER_ATTR_MAP[funkwhale_field.strip()] = ldap_field.strip()

    # Determine root DN supporting multiple root DNs
    AUTH_LDAP_ROOT_DN = env("LDAP_ROOT_DN")
    AUTH_LDAP_ROOT_DN_LIST = []
    for ROOT_DN in AUTH_LDAP_ROOT_DN.split():
        AUTH_LDAP_ROOT_DN_LIST.append(
            LDAPSearch(ROOT_DN, ldap.SCOPE_SUBTREE, AUTH_LDAP_SEARCH_FILTER)
        )
    # Search for the user in all the root DNs
    AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(*AUTH_LDAP_ROOT_DN_LIST)

    # Search for group types
    LDAP_GROUP_DN = env("LDAP_GROUP_DN", default="")
    if LDAP_GROUP_DN:
        AUTH_LDAP_GROUP_DN = LDAP_GROUP_DN
        # Get filter
        AUTH_LDAP_GROUP_FILTER = env("LDAP_GROUP_FILER", default="")
        # Search for the group in the specified DN
        AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
            AUTH_LDAP_GROUP_DN, ldap.SCOPE_SUBTREE, AUTH_LDAP_GROUP_FILTER
        )
        AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

        # Configure basic group support
        LDAP_REQUIRE_GROUP = env("LDAP_REQUIRE_GROUP", default="")
        if LDAP_REQUIRE_GROUP:
            AUTH_LDAP_REQUIRE_GROUP = LDAP_REQUIRE_GROUP
        LDAP_DENY_GROUP = env("LDAP_DENY_GROUP", default="")
        if LDAP_DENY_GROUP:
            AUTH_LDAP_DENY_GROUP = LDAP_DENY_GROUP


# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = "slugify.slugify"

CACHE_URL_DEFAULT = "redis://127.0.0.1:6379/0"
if IS_DOCKER_SETUP:
    CACHE_URL_DEFAULT = "redis://redis:6379/0"

CACHE_URL = env.str("CACHE_URL", default=CACHE_URL_DEFAULT)
"""
The URL of your redis server. For example:

- ``redis://<host>:<port>/<database>``
- ``redis://127.0.0.1:6379/0``
- ``redis://:password@localhost:6379/0``

If you're using password auth (the extra slash is important)
- ``redis:///run/redis/redis.sock?db=0`` over unix sockets

.. note::

    If you want to use Redis over unix sockets, you also need to update
    :attr:`CELERY_BROKER_URL`, because the scheme differs from the one used by
    :attr:`CACHE_URL`.

"""
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "funkwhale_api.common.cache.RedisClient",
            "IGNORE_EXCEPTIONS": True,  # mimics memcache behavior.
            # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        },
    },
    "local": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "local-cache",
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [CACHES["default"]["LOCATION"]]},
    }
}

CACHEOPS_DURATION = env("CACHEOPS_DURATION", default=0)
CACHEOPS_ENABLED = bool(CACHEOPS_DURATION)

if CACHEOPS_ENABLED:
    INSTALLED_APPS += ("cacheops",)
    CACHEOPS_REDIS = CACHE_URL
    CACHEOPS_PREFIX = lambda _: "cacheops"  # noqa
    CACHEOPS_DEFAULTS = {"timeout": CACHEOPS_DURATION}
    CACHEOPS = {
        "music.album": {"ops": "count"},
        "music.artist": {"ops": "count"},
        "music.track": {"ops": "count"},
    }

# CELERY
INSTALLED_APPS += ("funkwhale_api.taskapp.celery.CeleryConfig",)
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=CACHE_URL)
"""
The celery task broker URL. Defaults to :attr:`CACHE_URL`.
You don't need to tweak this unless you want
to use a different server or use Redis sockets to connect.

Example:

- ``unix://127.0.0.1:6379/0``
- ``redis+socket:///run/redis/redis.sock?virtual_host=0``

"""
# END CELERY
# Location of root django.contrib.admin URL, use {% url 'admin:index' %}

# Your common stuff: Below this line define 3rd party library settings
CELERY_TASK_DEFAULT_RATE_LIMIT = 1
CELERY_TASK_TIME_LIMIT = 300
CELERY_BEAT_SCHEDULE = {
    #"audio.fetch_rss_feeds": {
    #    "task": "audio.fetch_rss_feeds",
    #    "schedule": crontab(minute="0", hour="*"),
    #    "options": {"expires": 60 * 60},
    #},
    "common.prune_unattached_attachments": {
        "task": "common.prune_unattached_attachments",
        "schedule": crontab(minute="0", hour="*"),
        "options": {"expires": 60 * 60},
    },
    #"federation.clean_music_cache": {
    #    "task": "federation.clean_music_cache",
    #    "schedule": crontab(minute="0", hour="*/2"),
    #    "options": {"expires": 60 * 2},
    #},
    "music.clean_transcoding_cache": {
        "task": "music.clean_transcoding_cache",
        "schedule": crontab(minute="0", hour="*"),
        "options": {"expires": 60 * 2},
    },
    "oauth.clear_expired_tokens": {
        "task": "oauth.clear_expired_tokens",
        "schedule": crontab(minute="0", hour="0"),
        "options": {"expires": 60 * 60 * 24},
    },
    # "federation.refresh_nodeinfo_known_nodes": {
    #     "task": "federation.refresh_nodeinfo_known_nodes",
    #     "schedule": crontab(
    #         **env.dict(
    #             "SCHEDULE_FEDERATION_REFRESH_NODEINFO_KNOWN_NODES",
    #             default={"minute": "0", "hour": "*"},
    #         )
    #     ),
    #     "options": {"expires": 60 * 60},
    # },
    "music.library.schedule_remote_scan": {
        "task": "music.library.schedule_scan",
        "schedule": crontab(day_of_week="1", minute="0", hour="2"),
        "options": {"expires": 60 * 60 * 24},
    },
    # "federation.check_all_remote_instance_availability": {
    #     "task": "federation.check_all_remote_instance_availability",
    #     "schedule": crontab(
    #         **env.dict(
    #             "SCHEDULE_FEDERATION_CHECK_INTANCES_AVAILABILITY",
    #             default={"minute": "0", "hour": "*"},
    #         )
    #     ),
    #     "options": {"expires": 60 * 60},
    # },
    "typesense.build_canonical_index": {
        "task": "typesense.build_canonical_index",
        "schedule": crontab(day_of_week="*/2", minute="0", hour="3"),
        "options": {"expires": 60 * 60 * 24},
    },
}

if env.bool("ADD_ALBUM_TAGS_FROM_TRACKS", default=True):
    CELERY_BEAT_SCHEDULE["music.albums_set_tags_from_tracks"] = {
        "task": "music.albums_set_tags_from_tracks",
        "schedule": crontab(minute="0", hour="4", day_of_week="4"),
        "options": {"expires": 60 * 60 * 2},
    }

if env.bool("ADD_ARTIST_TAGS_FROM_TRACKS", default=True):
    CELERY_BEAT_SCHEDULE["music.artists_set_tags_from_tracks"] = {
        "task": "music.artists_set_tags_from_tracks",
        "schedule": crontab(minute="0", hour="4", day_of_week="4"),
        "options": {"expires": 60 * 60 * 2},
    }

NODEINFO_REFRESH_DELAY = env.int("NODEINFO_REFRESH_DELAY", default=3600 * 24)


def get_user_secret_key(user):
    from django.conf import settings

    return settings.SECRET_KEY + str(user.secret_key)


OLD_PASSWORD_FIELD_ENABLED = True
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": env.int("PASSWORD_MIN_LENGTH", default=8)},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
DISABLE_PASSWORD_VALIDATORS = env.bool("DISABLE_PASSWORD_VALIDATORS", default=False)
"""
Whether to disable password validation rules during registration.
Validators include password length, common words, similarity with username.
"""
if DISABLE_PASSWORD_VALIDATORS:
    AUTH_PASSWORD_VALIDATORS = []
ACCOUNT_ADAPTER = "funkwhale_api.users.adapters.FunkwhaleAccountAdapter"
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (
#     'localhost',
#     'funkwhale.localhost',
# )
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "funkwhale_api.common.pagination.FunkwhalePagination",
    "PAGE_SIZE": 25,
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "funkwhale_api.federation.parsers.ActivityParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "funkwhale_api.common.authentication.OAuth2Authentication",
        "funkwhale_api.common.authentication.ApplicationTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "funkwhale_api.users.oauth.permissions.ScopePermission",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.OrderingFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "NUM_PROXIES": env.int("NUM_PROXIES", default=1),
}
THROTTLING_ENABLED = env.bool("THROTTLING_ENABLED", default=True)
"""
Whether to enable throttling (also known as rate-limiting).
We recommend you leave this enabled to improve the quality
of the service, especially on public pods .
"""

if THROTTLING_ENABLED:
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = env.list(
        "THROTTLE_CLASSES",
        default=["funkwhale_api.common.throttling.FunkwhaleThrottle"],
    )

THROTTLING_SCOPES = {
    "*": {"anonymous": "anonymous-wildcard", "authenticated": "authenticated-wildcard"},
    "create": {
        "authenticated": "authenticated-create",
        "anonymous": "anonymous-create",
    },
    "list": {"authenticated": "authenticated-list", "anonymous": "anonymous-list"},
    "retrieve": {
        "authenticated": "authenticated-retrieve",
        "anonymous": "anonymous-retrieve",
    },
    "destroy": {
        "authenticated": "authenticated-destroy",
        "anonymous": "anonymous-destroy",
    },
    "update": {
        "authenticated": "authenticated-update",
        "anonymous": "anonymous-update",
    },
    "partial_update": {
        "authenticated": "authenticated-update",
        "anonymous": "anonymous-update",
    },
}

THROTTLING_USER_RATES = env.dict("THROTTLING_RATES", default={})

THROTTLING_RATES = {
    "anonymous-wildcard": {
        "rate": THROTTLING_USER_RATES.get("anonymous-wildcard", "1000/h"),
        "description": "Anonymous requests not covered by other limits",
    },
    "authenticated-wildcard": {
        "rate": THROTTLING_USER_RATES.get("authenticated-wildcard", "2000/h"),
        "description": "Authenticated requests not covered by other limits",
    },
    "authenticated-create": {
        "rate": THROTTLING_USER_RATES.get("authenticated-create", "1000/hour"),
        "description": "Authenticated POST requests",
    },
    "anonymous-create": {
        "rate": THROTTLING_USER_RATES.get("anonymous-create", "1000/day"),
        "description": "Anonymous POST requests",
    },
    "authenticated-list": {
        "rate": THROTTLING_USER_RATES.get("authenticated-list", "10000/hour"),
        "description": "Authenticated GET requests on resource lists",
    },
    "anonymous-list": {
        "rate": THROTTLING_USER_RATES.get("anonymous-list", "10000/day"),
        "description": "Anonymous GET requests on resource lists",
    },
    "authenticated-retrieve": {
        "rate": THROTTLING_USER_RATES.get("authenticated-retrieve", "10000/hour"),
        "description": "Authenticated GET requests on resource detail",
    },
    "anonymous-retrieve": {
        "rate": THROTTLING_USER_RATES.get("anonymous-retrieve", "10000/day"),
        "description": "Anonymous GET requests on resource detail",
    },
    "authenticated-destroy": {
        "rate": THROTTLING_USER_RATES.get("authenticated-destroy", "500/hour"),
        "description": "Authenticated DELETE requests on resource detail",
    },
    "anonymous-destroy": {
        "rate": THROTTLING_USER_RATES.get("anonymous-destroy", "1000/day"),
        "description": "Anonymous DELETE requests on resource detail",
    },
    "authenticated-update": {
        "rate": THROTTLING_USER_RATES.get("authenticated-update", "1000/hour"),
        "description": "Authenticated PATCH and PUT requests on resource detail",
    },
    "anonymous-update": {
        "rate": THROTTLING_USER_RATES.get("anonymous-update", "1000/day"),
        "description": "Anonymous PATCH and PUT requests on resource detail",
    },
    "subsonic": {
        "rate": THROTTLING_USER_RATES.get("subsonic", "2000/hour"),
        "description": "All subsonic API requests",
    },
    # potentially spammy / dangerous endpoints
    "authenticated-reports": {
        "rate": THROTTLING_USER_RATES.get("authenticated-reports", "100/day"),
        "description": "Authenticated report submission",
    },
    "anonymous-reports": {
        "rate": THROTTLING_USER_RATES.get("anonymous-reports", "10/day"),
        "description": "Anonymous report submission",
    },
    "authenticated-oauth-app": {
        "rate": THROTTLING_USER_RATES.get("authenticated-oauth-app", "10/hour"),
        "description": "Authenticated OAuth app creation",
    },
    "anonymous-oauth-app": {
        "rate": THROTTLING_USER_RATES.get("anonymous-oauth-app", "10/day"),
        "description": "Anonymous OAuth app creation",
    },
    "oauth-authorize": {
        "rate": THROTTLING_USER_RATES.get("oauth-authorize", "100/hour"),
        "description": "OAuth app authorization",
    },
    "oauth-token": {
        "rate": THROTTLING_USER_RATES.get("oauth-token", "100/hour"),
        "description": "OAuth token creation",
    },
    "oauth-revoke-token": {
        "rate": THROTTLING_USER_RATES.get("oauth-revoke-token", "100/hour"),
        "description": "OAuth token deletion",
    },
    "login": {
        "rate": THROTTLING_USER_RATES.get("login", "30/hour"),
        "description": "Login",
    },
    "signup": {
        "rate": THROTTLING_USER_RATES.get("signup", "10/day"),
        "description": "Account creation",
    },
    "verify-email": {
        "rate": THROTTLING_USER_RATES.get("verify-email", "20/h"),
        "description": "Email address confirmation",
    },
    "password-change": {
        "rate": THROTTLING_USER_RATES.get("password-change", "20/h"),
        "description": "Password change (when authenticated)",
    },
    "password-reset": {
        "rate": THROTTLING_USER_RATES.get("password-reset", "20/h"),
        "description": "Password reset request",
    },
    "password-reset-confirm": {
        "rate": THROTTLING_USER_RATES.get("password-reset-confirm", "20/h"),
        "description": "Password reset confirmation",
    },
    "fetch": {
        "rate": THROTTLING_USER_RATES.get("fetch", "200/d"),
        "description": "Fetch remote objects",
    },
}
THROTTLING_RATES = THROTTLING_RATES
"""
Throttling rates for specific endpoints and app features.
Tweak this if you're hitting rate limit issues or if you want
to reduce the consumption of specific endpoints. Takes
the format ``<endpoint name>=<number>/<interval>``.

Example:

- ``signup=5/d,password-reset=2/d,anonymous-reports=5/d``
"""

BROWSABLE_API_ENABLED = env.bool("BROWSABLE_API_ENABLED", default=False)
if BROWSABLE_API_ENABLED:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += (
        "rest_framework.renderers.BrowsableAPIRenderer",
    )

REST_AUTH_SERIALIZERS = {
    "PASSWORD_RESET_SERIALIZER": "funkwhale_api.users.serializers.PasswordResetSerializer",  # noqa
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "funkwhale_api.users.serializers.PasswordResetConfirmSerializer",  # noqa
}
REST_SESSION_LOGIN = False

ATOMIC_REQUESTS = False
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Whether we should use Apache, Nginx (or other) headers
# when serving audio files. Defaults to Nginx.
REVERSE_PROXY_TYPE = env("REVERSE_PROXY_TYPE", default="nginx")
"""
Set your reverse proxy type. This changes the headers the
API uses to serve audio files. Allowed values:

- ``nginx``
- ``apache2``
"""
assert REVERSE_PROXY_TYPE in ["apache2", "nginx"], "Unsupported REVERSE_PROXY_TYPE"

PROTECT_FILES_PATH = env("PROTECT_FILES_PATH", default="/_protected")
"""
The path used to process internal redirection
to the reverse proxy.

.. important::

    Don't insert a slash at the end of this path.
"""

MUSICBRAINZ_CACHE_DURATION = env.int("MUSICBRAINZ_CACHE_DURATION", default=300)
"""
Length of time in seconds to cache MusicBrainz results.
"""
MUSICBRAINZ_HOSTNAME = env("MUSICBRAINZ_HOSTNAME", default="musicbrainz.org")
"""
The hostname of your MusicBrainz instance. Change
this setting if you run your own server or use a mirror.
You can include a port number in the hostname.

Examples:

- ``mymusicbrainz.mirror``
- ``localhost:5000``

"""
# Custom Admin URL, use {% url 'admin:index' %}
ADMIN_URL = env("DJANGO_ADMIN_URL", default="^api/admin/")
"""
Path to the Django admin dashboard.

Examples:

- ``^api/admin/``
- ``^api/mycustompath/``

"""
CSRF_USE_SESSIONS = False
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

ACCOUNT_USERNAME_BLACKLIST = [
    "funkwhale",
    "library",
    "instance",
    "test",
    "status",
    "root",
    "admin",
    "owner",
    "superuser",
    "staff",
    "service",
    "me",
    "ghost",
    "_",
    "-",
    "hello",
    "contact",
    "inbox",
    "outbox",
    "shared-inbox",
    "shared_inbox",
    "actor",
] + env.list("ACCOUNT_USERNAME_BLACKLIST", default=[])
"""
List of usernames that can't be used for registration. Given as a list of strings.
"""
EXTERNAL_REQUESTS_VERIFY_SSL = env.bool("EXTERNAL_REQUESTS_VERIFY_SSL", default=True)
"""
Whether to enforce TLS certificate verification
when performing outgoing HTTP requests.

We recommend you leave this setting enabled.
"""
EXTERNAL_REQUESTS_TIMEOUT = env.int("EXTERNAL_REQUESTS_TIMEOUT", default=10)
"""
Default timeout for external requests.
"""

MUSIC_DIRECTORY_PATH = env("MUSIC_DIRECTORY_PATH", default=None)
"""
The path on your server where Funkwhale places
files from in-place imports. This path needs to be
readable by the webserver and ``api`` and ``worker``
processes.

.. important::

    Don’t insert a slash at the end of this path.

On Docker installations, we recommend you use the default ``/music`` path.
On Debian installations you can use any absolute path. Defaults to
``/srv/funkwhale/data/music``.

.. note::

    You need to add this path to your reverse proxy configuration.
    Add the directory to your ``/_protected/music`` server block.

"""
MUSIC_DIRECTORY_SERVE_PATH = env(
    "MUSIC_DIRECTORY_SERVE_PATH", default=MUSIC_DIRECTORY_PATH
)
"""
On Docker setups the value of :attr:`MUSIC_DIRECTORY_PATH`
may be different from the actual path on your server.
You can specify this path in your :file:`docker-compose.yml` file::

    volumes:
        - /srv/funkwhale/data/music:/music:ro

In this case, you need to set :attr:`MUSIC_DIRECTORY_SERVE_PATH`
to ``/srv/funkwhale/data/music``. The webserver needs to be
able to read this directory.

.. important::

    Don’t insert a slash at the end of this path.

"""
# When this is set to default=True, we need to re-enable migration music/0042
# to ensure data is populated correctly on existing pods
MUSIC_USE_DENORMALIZATION = env.bool("MUSIC_USE_DENORMALIZATION", default=True)

USERS_INVITATION_EXPIRATION_DAYS = env.int(
    "USERS_INVITATION_EXPIRATION_DAYS", default=14
)
"""
The number of days before a user invite expires.
"""

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    "square": [
        ("original", "url"),
        ("square_crop", "crop__400x400"),
        ("medium_square_crop", "crop__200x200"),
        ("small_square_crop", "crop__50x50"),
    ],
    "attachment_square": [
        ("original", "url"),
        ("medium_square_crop", "crop__200x200"),
        ("large_square_crop", "crop__600x600"),
    ],
}
VERSATILEIMAGEFIELD_SETTINGS = {
    "create_images_on_demand": False,
    "jpeg_resize_quality": env.int("THUMBNAIL_JPEG_RESIZE_QUALITY", default=95),
}
RSA_KEY_SIZE = 2048
# for performance gain in tests, since we don't need to actually create the
# thumbnails
CREATE_IMAGE_THUMBNAILS = env.bool("CREATE_IMAGE_THUMBNAILS", default=True)
# we rotate actor keys at most every two days by default
ACTOR_KEY_ROTATION_DELAY = env.int("ACTOR_KEY_ROTATION_DELAY", default=3600 * 48)
SUBSONIC_DEFAULT_TRANSCODING_FORMAT = (
    env("SUBSONIC_DEFAULT_TRANSCODING_FORMAT", default="mp3") or None
)
"""
The default format files are transcoded into when using the Subsonic
API.
"""
# extra tags will be ignored
TAGS_MAX_BY_OBJ = env.int("TAGS_MAX_BY_OBJ", default=30)
"""
Maximum number of tags that can be associated with an object.
Extra tags are ignored.
"""
FEDERATION_OBJECT_FETCH_DELAY = env.int(
    "FEDERATION_OBJECT_FETCH_DELAY", default=60 * 24 * 3
)
"""
The delay in minutes before a remote object is automatically
refetched when accessed in the UI.
"""
MODERATION_EMAIL_NOTIFICATIONS_ENABLED = env.bool(
    "MODERATION_EMAIL_NOTIFICATIONS_ENABLED", default=True
)
"""
Whether to enable email notifications to moderators and pod admins.
"""
FEDERATION_AUTHENTIFY_FETCHES = True
FEDERATION_SYNCHRONOUS_FETCH = env.bool("FEDERATION_SYNCHRONOUS_FETCH", default=True)
FEDERATION_DUPLICATE_FETCH_DELAY = env.int(
    "FEDERATION_DUPLICATE_FETCH_DELAY", default=60 * 50
)
"""
The delay in seconds between two manual fetches of the same remote object.
"""
INSTANCE_SUPPORT_MESSAGE_DELAY = env.int("INSTANCE_SUPPORT_MESSAGE_DELAY", default=15)
"""
The number of days before your pod shows the "support your pod" message.
The timer starts after the user signs up.
"""
FUNKWHALE_SUPPORT_MESSAGE_DELAY = env.int("FUNKWHALE_SUPPORT_MESSAGE_DELAY", default=15)
"""
The number of days before your pod shows the "support Funkwhale" message.
The timer starts after the user signs up.
"""

MIN_DELAY_BETWEEN_DOWNLOADS_COUNT = env.int(
    "MIN_DELAY_BETWEEN_DOWNLOADS_COUNT", default=60 * 60 * 6
)
"""
The required number of seconds between downloads of a track
by the same IP or user to be counted separately in listen statistics.
"""
MARKDOWN_EXTENSIONS = env.list("MARKDOWN_EXTENSIONS", default=["nl2br", "extra"])
"""
A list of markdown extensions to enable.

See `<https://python-markdown.github.io/extensions/>`_.
"""
LINKIFIER_SUPPORTED_TLDS = ["audio"] + env.list("LINKINFIER_SUPPORTED_TLDS", default=[])
"""
Additional TLDs to support with our markdown linkifier.
"""
EXTERNAL_MEDIA_PROXY_ENABLED = env.bool("EXTERNAL_MEDIA_PROXY_ENABLED", default=True)
"""
Whether to proxy attachment files hosted on third party pods and and servers.
We recommend you leave this set to ``true``. This reduces the risk of leaking
user browsing information and reduces the bandwidth used on remote pods.
"""
PODCASTS_THIRD_PARTY_VISIBILITY = env("PODCASTS_THIRD_PARTY_VISIBILITY", default="me")
"""
By default, only people who subscribe to a podcast RSS have access
to its episodes. Change to ``instance`` or ``everyone`` to change the
default visibility.

.. note::

    Changing this value only affect new podcasts.
"""
PODCASTS_RSS_FEED_REFRESH_DELAY = env.int(
    "PODCASTS_RSS_FEED_REFRESH_DELAY", default=60 * 60 * 24
)
"""
The delay in seconds between two fetch of RSS feeds.

A lower rate means new episodes are fetched sooner,
but requires more resources.
"""
# maximum items loaded through XML feed
PODCASTS_RSS_FEED_MAX_ITEMS = env.int("PODCASTS_RSS_FEED_MAX_ITEMS", default=250)
"""
Maximum number of RSS items to load in each podcast feed.
"""

IGNORE_FORWARDED_HOST_AND_PROTO = env.bool(
    "IGNORE_FORWARDED_HOST_AND_PROTO", default=True
)
"""
Use :attr:`FUNKWHALE_HOSTNAME` and :attr:`FUNKWHALE_PROTOCOL`
instead of request header.
"""

HASHING_ALGORITHM = "sha256"
HASHING_CHUNK_SIZE = 1024 * 100

"""
Typenses Settings
"""
TYPESENSE_API_KEY = env("TYPESENSE_API_KEY", default=None)
""" Typesense API key. This need to be defined in the .env file for Typenses to be activated."""
TYPESENSE_PORT = env("TYPESENSE_PORT", default="8108")
"""Typesense listening port"""
TYPESENSE_PROTOCOL = env("TYPESENSE_PROTOCOL", default="http")
"""Typesense listening protocol"""
TYPESENSE_HOST = env(
    "TYPESENSE_HOST",
    default="typesense" if IS_DOCKER_SETUP else "localhost",
)
"""
Typesense hostname. Defaults to `localhost` on non-Docker deployments and to `typesense` on
Docker deployments.
"""
TYPESENSE_NUM_TYPO = env("TYPESENSE_NUM_TYPO", default=5)
