from neomodel import (
    StructuredNode, UniqueIdProperty, StringProperty, StructuredRel,
    DateTimeProperty, RelationshipFrom, RelationshipTo
)

from accounts.graphs import UserWritesComment, UserLikesComment


class CommentWrittenOnTweet(StructuredRel):
    """Relationship when Commment is added on Tweet"""
    rel_name = 'WRITTEN_ON'
    created_at = DateTimeProperty(default_now=True)


class Comment(StructuredNode):
    """Node Comment which is added on Node Tweet"""
    pk = UniqueIdProperty()
    text = StringProperty()

    user = RelationshipFrom(
        'accounts.graphs.User', UserWritesComment.rel_name, model=UserWritesComment
    )
    tweet = RelationshipTo(
        'feed.graphs.Tweet', CommentWrittenOnTweet.rel_name, model=CommentWrittenOnTweet
    )

    """Users who liked a comment"""
    users_liked = RelationshipFrom(
        'accounts.graphs.User', UserLikesComment.rel_name, model=UserLikesComment
    )
