"""

    This script will contain all mixn functions for project.

"""
import random
import uuid
from mimetypes import MimeTypes
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from hashids import Hashids
from rest_framework_simplejwt.tokens import RefreshToken

from ..__init__ import token_prefix
from models.user.models import UserDetail


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def generate_random_number(num=1000000):
    return str(random.randrange(num))


def generate_unique_code():
    hashids = Hashids()
    return hashids.encode(int(generate_random_number())).upper()


def generate_custom_uuid():
    return uuid.uuid4()


def check_file_extension(file):
    mime = MimeTypes()
    check = list(mime.guess_type(file.name))
    if len(check):
        if check[0].split('/')[0] == 'video':
            return True
    return False


def return_file_extension(file):
    mime = MimeTypes()
    check = list(mime.guess_type(file.name))
    if len(check):
        return check[0].split('/')[0]
    return ''


def capture_auth_image(url):
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urlopen(url).read())
    img_temp.flush()
    return img_temp


def update_user_auth_provider(user, provider, auth_id):
    ud = UserDetail.custom_manager.alive().filter(user=user).first()
    if not ud.facebook_profile_id and provider.upper() == 'FACEBOOK':
        ud.facebook_profile_id = auth_id
        ud.save()
    if not ud.google_profile_id and provider.upper() == 'GOOGLE':
        ud.google_profile_id = auth_id
        ud.save()
    return


def create_token(user):
    token = RefreshToken.for_user(user)

    prepare = {
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'token': token_prefix + str(token.access_token),
        'is_admin': user.is_superuser,
        'user_type': {
            'id': user.user_type.id,
            'name': user.user_type.name
        } if user.user_type else None
    }
    return prepare
