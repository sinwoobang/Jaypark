from neomodel import (
    StructuredNode, RelationshipFrom, RelationshipTo, StringProperty,
    IntegerProperty, DateTimeProperty, StructuredRel, UniqueIdProperty
)


class UserWritesTweet(StructuredRel):
    """Relationship when User tweets."""
    created_at = DateTimeProperty(default_now=True)


class UserFollows(StructuredRel):
    """Relationship when User follows someone."""
    created_at = DateTimeProperty(default_now=True)


class UserLikesTweet(StructuredRel):
    """Relationship when User likes a tweet."""
    created_at = DateTimeProperty(default_now=True)


class User(StructuredNode):
    """Node User"""
    pk = IntegerProperty(unique_index=True, required=True)
    username = StringProperty(unique_index=True, required=True)

    following = RelationshipTo('User', 'FOLLOWS')
    followed = RelationshipFrom('User', 'FOLLOWS', model=UserFollows)

    tweets_written = RelationshipTo('Tweet', 'WRITES_TWEET')
    tweets_liked = RelationshipTo('Tweet', 'LIKES_TWEET')

    def get_db_object(self):
        """Get a object in DB"""
        from accounts.models import User as DBUser
        return DBUser.objects.get(id=self.pk)

    def sync_with_db(self):
        """Synchronize self with DB data"""
        user = self.get_db_object()
        self.username = user.username
        self.save()


class Tweet(StructuredNode):
    """Node Tweet"""
    pk = UniqueIdProperty()
    text = StringProperty(required=True)
    user = RelationshipFrom('User', 'WRITES_TWEET', model=UserWritesTweet)

    """Users who liked a tweet."""
    liked_users = RelationshipFrom('User', 'LIKES_TWEET', model=UserLikesTweet)
