import datetime

from accounts.models import User


def default_profile_photo_url(request):
    """DEFAULT_PROFILE_PHOTO_URL will be set on context processors."""
    return {
        'DEFAULT_PROFILE_PHOTO_URL': User.DEFAULT_PROFILE_PHOTO_URL
    }


def datetimes(request):
    return {
        'now': datetime.datetime.now()
    }
