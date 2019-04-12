import logging

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from accounts.models import User
from common.utils import cypher_query_as_dict

logger = logging.getLogger('debugging')


@login_required
def feed(request):
    """The View Main Feed which is personalized."""
    user = request.user
    user_node = user.get_or_create_node()
    followings_nodes = user_node.following.all()
    followeds_nodes = user_node.followed.all()

    logger.info('following {}'.format(followings_nodes))
    logger.info('followed {}'.format(followeds_nodes))

    ct = {'user': user}
    return render(request, 'feed/index.html', ct)


@login_required
def feed_user(request, username):
    """The View User Feed for a specific user."""
    is_me = request.user.username == username  # if the user who is finding is the user logged in.
    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User not found.")

    """The below codes have used a raw query to order by Relationship."""
    query_params = {'target_user_pk': target_user.id}
    tweets_nodes = cypher_query_as_dict("""MATCH (USER)-[written_tweets:WRITES_TWEET]->(TWEET)
WHERE USER.pk = {target_user_pk}
RETURN TWEET.pk as pk, TWEET.text as text, toInt(written_tweets.created_at * 1000) as created_at
ORDER BY written_tweets.created_at DESC""", params=query_params)

    logger.debug('tweets : {}'.format(tweets_nodes))

    ct = {
        'user': request.user, 'target_user': target_user, 'tweets': tweets_nodes,
        'is_me': is_me,
    }
    return render(request, 'feed/user.html', ct)

