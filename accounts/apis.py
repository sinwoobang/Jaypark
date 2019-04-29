import json
import logging
from json import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from accounts.forms import UserCreationForm
from accounts.graphs import User as UserNode
from common.models import Image

User = get_user_model()
logger = logging.getLogger('debugging')


@require_http_methods(['POST'])
@csrf_exempt
def login(request):
    """
    Login API for non-web environment.(Especially for testing.)
    """
    try:
        body_data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_body',
            'status_message': 'No json data exists.'
        })

    form = AuthenticationForm(data=body_data)
    if not form.is_valid():
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': 'Please check your username or password.'
        })
    user = form.get_user()
    auth_login(request, user)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': '',
        'contents': {'user': {'id': user.id, 'username': user.username}}
    })


@require_http_methods(['POST'])
@csrf_exempt
def register(request):
    """
    Register API for non-web environment.(Especially for testing.)
    """
    try:
        body_data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_body',
            'status_message': 'No json data exists.'
        })

    with transaction.atomic():  # Queries will be committed if the below codes run without error.
        reg_form = UserCreationForm(data=body_data)  # register
        if reg_form.is_valid():  # if get succeed to register then login the user.
            reg_form.save()

            username = body_data['username']
            password = body_data['password1']
            user = authenticate(request=request, username=username, password=password)
            auth_login(request, user)

            try:
                user.create_node()
            except Exception as e:
                logger.error('FAIL TO CREATE A USER NODE FOR {u}, {e}'.format(u=username, e=e))

            return JsonResponse({
                'status': 'success',
                'status_code': '',
                'status_message': ''
            })

    logger.info(reg_form.errors)

    return JsonResponse({
        'status': 'error',
        'status_code': 'invalid_data',
        'status_message': 'Please check your input.'
    })


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
        'status_message': f'Now you are following {target_user.username}.'
    })


@require_http_methods(['POST'])
@login_required
def update(request):
    """
    Update Profile API that updates the photo and some features in the future.
    """
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_file',
            'status_message': 'No file exists.'
        })

    image = Image(image=file)
    image.save()

    image_url = image.image.url
    user_node = request.user.get_or_create_node()
    user_node.profile_photo_url = image_url
    user_node.save()

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': '',
        'contents': {
            'profile_photo_url': image_url
        }
    })
