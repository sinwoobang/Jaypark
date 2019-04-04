import json
import logging
from json import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


logger = logging.getLogger('debugging')


@require_http_methods(['POST'])
@login_required
def write(request):
    """Writing a post API"""
    try:
        body_data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_body',
            'status_message': 'No json data exists.'
        })

    text = body_data.get('text', None)
    if not text:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': 'Data `text` is required.'
        })

    logger.info(text)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': ''
    })
