from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username and password are required. Other fields are optional.
    """
    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        db_table = 'auth_user'

    def get_node_or_none(self):
        """Get a node in Graph"""
        from accounts.graphs import User as UserNode
        return UserNode.nodes.get_or_none(pk=self.id)

    def get_or_create_node(self):
        """Get a node but if it doesn't exist, create a node"""
        node = self.get_node_or_none()
        if not node:
            node = self.create_node()
        return node

    def create_node(self):
        """Create a node in Graph"""
        from accounts.graphs import User as UserNode
        return UserNode(pk=self.id, username=self.username).save()

    def has_profile_photo(self):
        """
        Check the value of UserNode.profile_photo_url is None or not.
        :return: True if it has it or False
        :rtype: bool
        """
        return self.get_or_create_node().has_profile_photo()

    def get_profile_photo_url(self):
        """Get the url of the photo of Profile"""
        return self.get_or_create_node().profile_photo_url

