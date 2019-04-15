import json
import logging
from json import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from neomodel import db as graphdb, DoesNotExist as NodeDoesNotExist, UniqueProperty

from feed.graphs import Tweet, Tag
from common.utils import extract_hashtags
from post.graphs import Comment as CommentNode

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

        try:  # Parse tags
            tags = extract_hashtags(text)
            for tag in tags:
                try:
                    tag_node = Tag(tag=tag).save()
                except UniqueProperty:
                    tag_node = Tag.nodes.get(tag=tag)
                tweet.tags.connect(tag_node)
        except Exception as e:  # to prevent to be input a weird string
            logger.error(f'Failed to parse tags : {text} {str(e)}')

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
                'id': tweet.pk
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
            'status_code': 'never_liked',
            'status_message': 'You never liked this tweet.'
        })

    user_node.tweets_liked.disconnect(tweet_node)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': ''
    })


@require_http_methods(['POST'])
@login_required
def write_comment(request):
    """Comment Writing API"""
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

    text = body_data.get('text', None)
    if not text:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': '`text` is required.'
        })

    user_node = request.user.get_or_create_node()
    try:
        tweet_node = Tweet.nodes.get(pk=tweet_id)
    except NodeDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'status_code': 'tweet_none',
            'status_message': 'The tweet does not exist.'
        })

    graphdb.begin()
    comment_node = CommentNode(text=text).save()
    comment_node.tweet.connect(tweet_node)
    comment_node.user.connect(user_node)
    graphdb.commit()

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': 'A comment was written.',
        'contents': {
            'comment': {'id': comment_node.pk}
        }
    })


@require_http_methods(['POST'])
@login_required
def like_comment(request):
    """Comment Like API"""
    try:
        body_data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_body',
            'status_message': 'No json data exists.'
        })

    comment_id = body_data.get('comment_id', None)
    if not comment_id:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': '`comment_id` is required.'
        })

    comment_node = CommentNode.nodes.get_or_none(pk=comment_id)
    if not comment_node:
        return JsonResponse({
            'status': 'error',
            'status_code': 'comment_none',
            'status_message': 'The comment does not exist.'
        })

    user_node = request.user.get_or_create_node()
    if user_node.comments_liked.is_connected(comment_node):
        return JsonResponse({
            'status': 'error',
            'status_code': 'already_liked',
            'status_message': 'You already liked this comment.'
        })

    user_node.comments_liked.connect(comment_node)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': 'Your like was reflected.'
    })


@require_http_methods(['POST'])
@login_required
def unlike_comment(request):
    """Comment UnLike API"""
    try:
        body_data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_body',
            'status_message': 'No json data exists.'
        })

    comment_id = body_data.get('comment_id', None)
    if not comment_id:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': '`comment_id` is required.'
        })

    comment_node = CommentNode.nodes.get_or_none(pk=comment_id)
    if not comment_node:
        return JsonResponse({
            'status': 'error',
            'status_code': 'comment_none',
            'status_message': 'The comment does not exist.'
        })

    user_node = request.user.get_or_create_node()
    if not user_node.comments_liked.is_connected(comment_node):
        return JsonResponse({
            'status': 'error',
            'status_code': 'never_liked',
            'status_message': 'You never liked this comment.'
        })

    user_node.comments_liked.disconnect(comment_node)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': 'Your unlike was reflected.'
    })
