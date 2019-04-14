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


class TweetHasTag(StructuredRel):
    """Relationship when Tweet has a tag."""
    pass


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

    """Tags which is written a tweet."""
    tags = RelationshipTo('Tag', 'HAS_TAG', model=TweetHasTag)

    """Users who liked a tweet."""
    users_liked = RelationshipFrom('User', 'LIKES_TWEET', model=UserLikesTweet)


class Tag(StructuredNode):
    """Node Tag which is known as HashTag"""
    pk = UniqueIdProperty()
    tag = StringProperty(required=True, unique_index=True)
    created_at = DateTimeProperty(default_now=True)

    """Tweets which has this tag."""
    tweets_has = RelationshipFrom('Tweet', 'HAS_TAG', model=TweetHasTag)
