from neomodel import (
    StructuredNode, RelationshipFrom, RelationshipTo, StringProperty,
    UniqueIdProperty, IntegerProperty
)


class User(StructuredNode):
    """Node User"""
    uid = UniqueIdProperty()
    pk = IntegerProperty(unique_index=True, required=True)
    username = StringProperty(unique_index=True, required=True)

    following = RelationshipTo('User', 'FOLLOWING')
    followed = RelationshipFrom('User', 'FOLLOWED')
