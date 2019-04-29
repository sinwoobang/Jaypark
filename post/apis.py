import datetime
import json
import logging
from json import JSONDecodeError

from django.utils.timesince import timesince

from accounts.models import User
from common.utils.etc import datetime2timestamp
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from neomodel import db as graphdb, DoesNotExist as NodeDoesNotExist, UniqueProperty

from feed.graphs import Tweet, Tag, TweetScoreType
from post.graphs import Comment as CommentNode
from common.utils.etc import extract_hashtags
from post.models import ScoringHistory, ScoringHistoryType

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
        score = user_node.get_score()
        tweet = Tweet(text=text, score=score).save()
        tweet.user.connect(user_node)
        graphdb.commit()

        ScoringHistory.objects.create(
            user=request.user,
            tweet_id=tweet.pk,
            type=ScoringHistoryType.POST_COMMENT.value,
            cumulative_score=score, delta_score=score
        )
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

    current_score = tweet_node.score or 0
    type = TweetScoreType.LIKED.name
    delta_score = TweetScoreType.LIKED.value
    cumulative_score = current_score + delta_score

    tweet_node.score = cumulative_score
    tweet_node.save()

    ScoringHistory.objects.create(
        user=request.user,
        tweet_id=tweet_node.pk,
        type=type,
        cumulative_score=cumulative_score, delta_score=delta_score
    )

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

    current_score = tweet_node.score or 0
    type = TweetScoreType.UNLIKED.name
    delta_score = TweetScoreType.UNLIKED.value
    cumulative_score = current_score + delta_score

    tweet_node.score = cumulative_score
    tweet_node.save()

    ScoringHistory.objects.create(
        user=request.user,
        tweet_id=tweet_node.pk,
        type=type,
        cumulative_score=cumulative_score, delta_score=delta_score
    )

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

    current_score = tweet_node.score or 0
    type = TweetScoreType.COMMENTED.name
    delta_score = TweetScoreType.COMMENTED.value
    cumulative_score = current_score + delta_score

    tweet_node.score = cumulative_score
    tweet_node.save()

    ScoringHistory.objects.create(
        user=request.user,
        tweet_id=tweet_node.pk,
        type=type,
        cumulative_score=cumulative_score, delta_score=delta_score
    )

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


@require_http_methods(['GET'])
def get_comments(request):
    """Get Comments API"""
    tweet_id = request.GET.get('tweet_id')
    if not tweet_id:
        return JsonResponse({
            'status': 'error',
            'status_code': 'invalid_data',
            'status_message': '`tweet_id` is required.'
        })

    try:
        tweet = Tweet.nodes.get(pk=tweet_id)
        writes_relationship = tweet.comments_written
        comments_nodes = tweet.comments_written.all()
    except Tweet.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'status_code': 'tweet_none',
            'status_message': 'The tweet does not exist.'
        })

    comments = []
    for comment_node in comments_nodes:
        created_at = writes_relationship.relationship(comment_node).created_at.replace(tzinfo=None)
        print(datetime.datetime.now())
        comment_user_node = comment_node.user.get()
        comment_user = User(username=comment_user_node.username)
        comment = {
            'id': comment_node.pk,
            'text': comment_node.text,
            'user': {
                'id': comment_node.id,
                'username': comment_user_node.username,
                'profile_url': comment_user.get_profile_url(),
                'profile_photo_url':
                    comment_user_node.profile_photo_url or User.DEFAULT_PROFILE_PHOTO_URL
            },
            'timesince': timesince(created_at, now=datetime.datetime.now()),
            'created_at': datetime2timestamp(created_at)
        }
        comments.append(comment)
    comments.sort(key=lambda c: ['created_at'], reverse=True)

    return JsonResponse({
        'status': 'success',
        'status_code': '',
        'status_message': '',
        'contents': {
            'comments': comments
        }
    })
