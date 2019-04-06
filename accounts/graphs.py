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

    def get_db_object(self):
        """Get a object in DB"""
        from accounts.models import User as DBUser
        return DBUser.objects.get(id=self.pk)

    def sync_with_db(self):
        """Synchronize self with DB data"""
        user = self.get_db_object()
        self.username = user.username
        self.save()
