from enum import Enum

from neomodel import (
    StructuredNode, RelationshipFrom, RelationshipTo, StringProperty,
    IntegerProperty, DateTimeProperty, StructuredRel
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


class UserWritesComment(StructuredRel):
    """Relationship when User writes a comment on a tweet."""
    rel_name = 'WRITES'
    created_at = DateTimeProperty(default_now=True)


class UserLikesComment(StructuredRel):
    """Relationship when User likes a comment on a tweet."""
    rel_name = 'LIKES'
    created_at = DateTimeProperty(default_now=True)


class UserScoreType(Enum):
    """Enum Score types corresponding to User's status"""
    EACH_FOLLOWED = 300


class User(StructuredNode):
    """Node User"""
    pk = IntegerProperty(unique_index=True, required=True)
    username = StringProperty(unique_index=True, required=True)
    profile_photo_url = StringProperty()

    following = RelationshipTo('User', 'FOLLOWS')
    followed = RelationshipFrom('User', 'FOLLOWS', model=UserFollows)

    tweets_written = RelationshipTo('feed.graphs.Tweet', 'WRITES_TWEET')
    tweets_liked = RelationshipTo('feed.graphs.Tweet', 'LIKES_TWEET')

    comments_written = RelationshipTo(
        'post.graphs.Comment', UserWritesComment.rel_name, model=UserWritesComment
    )
    comments_liked = RelationshipTo(
        'post.graphs.Comment', UserLikesComment.rel_name, model=UserLikesComment
    )

    def get_db_object(self):
        """Get a object in DB"""
        from accounts.models import User as DBUser
        return DBUser.objects.get(id=self.pk)

    def get_score(self):
        """
        The influence score of a user
        It will be used as the base score of Tweet.
        """
        return len(self.nodes.followed.all()) * UserScoreType.EACH_FOLLOWED.value

    def has_profile_photo(self):
        return bool(self.profile_photo_url)

    def sync_with_db(self):
        """Synchronize self with DB data"""
        user = self.get_db_object()
        self.username = user.username
        self.save()
