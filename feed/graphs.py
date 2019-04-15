from neomodel import (
    StructuredNode, UniqueIdProperty, StringProperty, RelationshipFrom,
    RelationshipTo, DateTimeProperty, StructuredRel
)

from accounts.graphs import UserWritesTweet, UserLikesTweet
from post.graphs import CommentWrittenOnTweet


class TweetHasTag(StructuredRel):
    """Relationship when Tweet has a tag."""
    pass


class Tweet(StructuredNode):
    """Node Tweet"""
    pk = UniqueIdProperty()
    text = StringProperty(required=True)
    user = RelationshipFrom('accounts.graphs.User', 'WRITES_TWEET', model=UserWritesTweet)

    """Tags which is written a tweet."""
    tags = RelationshipTo('Tag', 'HAS_TAG', model=TweetHasTag)

    """Users who liked a tweet."""
    users_liked = RelationshipFrom('accounts.graphs.User', 'LIKES_TWEET', model=UserLikesTweet)

    """Comments which are written on a tweet."""
    comments_written = RelationshipFrom(
        'post.graphs.Comment', CommentWrittenOnTweet.rel_name, model=CommentWrittenOnTweet
    )


class Tag(StructuredNode):
    """Node Tag which is known as HashTag"""
    pk = UniqueIdProperty()
    tag = StringProperty(required=True, unique_index=True)
    created_at = DateTimeProperty(default_now=True)

    """Tweets which has this tag."""
    tweets_has = RelationshipFrom('Tweet', 'HAS_TAG', model=TweetHasTag)
