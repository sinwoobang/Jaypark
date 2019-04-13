import json
import logging
from json import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from neomodel import db as graphdb, DoesNotExist as NodeDoesNotExist

from accounts.graphs import Tweet


logger = logging.getLogger('debugging')


@require_http_methods(['POST'])
@login_required
def write(request):
    """Tweet Writing API"""
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

    graphdb.begin()  # Set a save point to make a relationship between a user and a tweet.
    try:
        user_node = request.user.get_or_create_node()
        tweet = Tweet(text=text).save()
        tweet.user.connect(user_node)
        graphdb.commit()
    except Exception as e:
        logger.error(e)
        graphdb.rollback()

        return JsonResponse({
            'status': 'error',
            'status_code': 'tweet_failed',
            'status_message': 'Failed to tweet.'
        })

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': '',
        'contents': {
            'tweet': {
                'pk': tweet.pk
            }
        }
    })


@require_http_methods(['POST'])
@login_required
def like(request):
    """Tweet Like API"""
    try:
        body_data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_body',
            'status_message': 'No json data exists.'
        })

    tweet_id = body_data.get('tweet_id', None)
    if not tweet_id:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': '`tweet_id` is required.'
        })

    try:
        tweet_node = Tweet.nodes.get(pk=tweet_id)
    except NodeDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'status_code': 'tweet_none',
            'status_message': 'The tweet does not exist.'
        })

    user_node = request.user.get_or_create_node()
    if user_node.tweets_liked.is_connected(tweet_node):
        return JsonResponse({
            'status': 'error',
            'status_code': 'already_liked',
            'status_message': 'You already liked this tweet.'
        })

    user_node.tweets_liked.connect(tweet_node)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': ''
    })


@require_http_methods(['POST'])
@login_required
def unlike(request):
    """Tweet UnLike API"""
    try:
        body_data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_body',
            'status_message': 'No json data exists.'
        })

    tweet_id = body_data.get('tweet_id', None)
    if not tweet_id:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': '`tweet_id` is required.'
        })

    try:
        tweet_node = Tweet.nodes.get(pk=tweet_id)
    except NodeDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'status_code': 'tweet_none',
            'status_message': 'The tweet does not exist.'
        })

    user_node = request.user.get_or_create_node()
    if not user_node.tweets_liked.is_connected(tweet_node):
        return JsonResponse({
            'status': 'error',
            'status_code': 'already_liked',
            'status_message': 'You never liked this tweet.'
        })

    user_node.tweets_liked.disconnect(tweet_node)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': ''
    })
