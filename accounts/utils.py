import uuid

from django.contrib.auth import get_user_model
from neomodel import UniqueProperty

from accounts.graphs import User as UserNode


User = get_user_model()


def sync_db_users_to_graph():
    """
    Synchronize all users in database to graphs.
    :return:
    """
    users = User.objects.all()
    for u in users:
        try:
            UserNode(username=u.username, pk=u.id).save()
        except UniqueProperty:
            user_node = UserNode.nodes.get(username=u.username)
            user_node.username = u.username
            user_node.pk = u.id
            user_node.save()


def generate_photo_profile_path(instance, filename):
    """
    Generate the url of the photo of profile.
    The below params are the format of Django ImageField.
    :param instance:
    :param filename:
    :return:
    """
    return 'photo/profile/{}'.format(uuid.uuid4().hex)
