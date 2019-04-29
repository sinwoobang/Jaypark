import logging

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from accounts.models import User
from feed.utils import get_user_tweets
from common.utils.etc import cypher_query_as_dict

logger = logging.getLogger('debugging')


@login_required
def feed(request):
    """The View Main Feed which is personalized."""
    user = request.user
    user_node = user.get_or_create_node()
    number_followings = len(user_node.following.all())
    number_followeds = len(user_node.followed.all())

    """Get following's tweets"""
    followings_tweets_query = """
MATCH (user:User {pk: {user_pk}})-[:FOLLOWS]->(following)-[w:WRITES_TWEET]->(TWEET)
OPTIONAL MATCH (user)-[l:LIKES_TWEET]->(TWEET)
RETURN following.pk as following_pk, following.username as following_username,
    following.profile_photo_url as profile_photo_url, 
    TWEET as tweet, toInt(w.created_at * 1000) as created_at,
    l IS NOT NULL as is_liked"""
    followings_tweets_nodes = cypher_query_as_dict(
        followings_tweets_query,
        params={'user_pk': user.id}
    )
    logger.debug(followings_tweets_nodes)

    my_tweets_nodes = get_user_tweets(user.id)  # tweets which are posted by me.
    logger.debug(my_tweets_nodes)

    """The below codes will compose feed."""
    feed_tweets = []  # A list that contains contents which composes feed.
    for node in followings_tweets_nodes:
        _user_id = node['following_pk']  # To distinguish a writer and the login user
        is_me = _user_id == user.id
        username = node['following_username']
        profile_photo_url = node['profile_photo_url'] or User.DEFAULT_PROFILE_PHOTO_URL

        tweet_id = node['tweet']['pk']
        text = node['tweet']['text']
        score = node['tweet']['score'] or 0

        is_liked = node['is_liked']
        created_at = node['created_at']

        tweet = {
            'user_id': _user_id, 'username': username, 'tweet_id': tweet_id, 'text': text,
            'is_me': is_me, 'is_liked': is_liked, 'score': score, 'created_at': created_at,
            'profile_photo_url': profile_photo_url
        }
        feed_tweets.append(tweet)

    for node in my_tweets_nodes:
        _user_id = node['user_pk']  # To distinguish a writer and the login user
        is_me = _user_id == user.id
        username = node['username']
        profile_photo_url = node['profile_photo_url'] or User.DEFAULT_PROFILE_PHOTO_URL

        tweet_id = node['pk']
        text = node['text']
        score = node['score'] or 0

        is_liked = node['is_liked']
        created_at = node['created_at']

        tweet = {
            'user_id': _user_id, 'username': username, 'tweet_id': tweet_id, 'text': text,
            'is_me': is_me, 'is_liked': is_liked, 'score': score, 'created_at': created_at,
            'profile_photo_url': profile_photo_url
        }
        feed_tweets.append(tweet)
    feed_tweets.sort(key=lambda c: c['score'] + c['created_at'], reverse=True)

    ct = {
        'user': user, 'feed_tweets': feed_tweets,
        'number_followings': number_followings,
        'number_followeds': number_followeds
    }
    return render(request, 'feed/index.html', ct)


@login_required
def feed_user(request, username):
    """The View User Feed for a specific user."""
    is_me = request.user.username == username  # if the user who is finding is the user logged in.
    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User not found.")

    tweets_nodes = get_user_tweets(target_user.id, 'created_at')

    logger.debug('tweets : {}'.format(tweets_nodes))

    ct = {
        'user': request.user, 'target_user': target_user, 'tweets': tweets_nodes,
        'is_me': is_me,
    }
    return render(request, 'feed/user.html', ct)

