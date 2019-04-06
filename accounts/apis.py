import json
import logging
from json import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from accounts.graphs import User as UserNode

User = get_user_model()
logger = logging.getLogger('debugging')


@require_http_methods(['POST'])
@login_required
def follow(request):
    """
    Following API that follow someone.

    request.GET
    - key(str) : The value is 'username' or 'user_id'.
        It determines which field will be used for finding a user.
    - username(str) : A username to find a user.
    - user_id(int) : A user id username to find a user.
    """
    try:
        body_data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_body',
            'status_message': 'No json data exists.'
        })

    user_filter = {}
    key = body_data.get('key')
    if key == 'username':
        username = body_data.get('username', None)
        if not username:
            return JsonResponse({
                'status': 'error',
                'status_code': 'invalid_data',
                'status_message': 'Data `username` is required.'
            })

        user_filter['username'] = username
    elif key == 'user_id':
        try:
            user_id = int(body_data.get('user_id', None))
        except (ValueError, TypeError):
            return JsonResponse({
                'status': 'error',
                'status_code': 'invalid_data',
                'status_message': 'Data `user_id` is required.'
            })
        user_filter['user_id'] = user_id
    else:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': 'Data `key` is invalid.'
        })

    try:
        target_user = User.objects.get(**user_filter)
        target_user_node = target_user.get_or_create_node()
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': 'The target user does not exist.'
        })

    user_node = UserNode.nodes.get(username=request.user.username)
    user_node.following.connect(target_user_node)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': ''
    })
