import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


logger = logging.getLogger('debugging')


@login_required
def feed(request):
    user = request.user
    user_node = user.get_or_create_node()
    followings_nodes = user_node.following.all()
    followeds_nodes = user_node.followed.all()

    logger.info('following {}'.format(followings_nodes))
    logger.info('followed {}'.format(followeds_nodes))

    ct = {'user': user}
    return render(request, 'feed/index.html', ct)
