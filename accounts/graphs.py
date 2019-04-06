from neomodel import (
    StructuredNode, RelationshipFrom, RelationshipTo, StringProperty,
    UniqueIdProperty
)


class User(StructuredNode):
    """Node User"""
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)

    following = RelationshipTo('User', 'FOLLOWING')
    followed = RelationshipFrom('User', 'FOLLOWED')
