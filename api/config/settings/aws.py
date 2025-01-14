from os import getenv
from urllib.parse import urlparse

import requests

from .common import *

STAGE = 'prod'

EC2_PRIVATE_IPS = []
METADATA_URI = getenv('ECS_CONTAINER_METADATA_URI_V4')

ADMINS = (
    ('Jacob', 'jacobef10@gmail.com'),
)
MANAGERS = (
    ('Jacob', 'jacobef10@gmail.com'),
)

SECRET_KEY = getenv('DJANGO_SECRET_KEY')

def filter_transactions(event, hint):
    url_string = event["request"]["url"]
    parsed_url = urlparse(url_string)

    if "/health" in parsed_url.path:
        return None

    return event


try:
    resp = requests.get(METADATA_URI + '/task')
    data = resp.json()

    for container in data['Containers']:
        for network in container['Networks']:
            EC2_PRIVATE_IPS.extend(network['IPv4Addresses'])

except Exception as e:
    # silently fail as we may not be in an ECS environment
    print(e)
    pass

if EC2_PRIVATE_IPS:
    # Be sure your ALLOWED_HOSTS is a list NOT a tuple
    # or .append() will fail
    ALLOWED_HOSTS.extend(EC2_PRIVATE_IPS)

ALLOWED_HOSTS += ['.sacredsound.app', 'sacredsound.app']

CSRF_TRUSTED_ORIGINS = ['https://*.sacredsound.app']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('DB_NAME'),
        'USER': getenv('DB_USERNAME'),
        'PASSWORD': getenv('DB_PASSWORD'),
        'HOST': getenv('DB_HOSTNAME')
    }
}

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
AWS_STORAGE_BUCKET_NAME = getenv('S3_BUCKET')

TYPESENSE_HOST = "typesense"