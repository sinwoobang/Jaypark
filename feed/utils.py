from common.utils import cypher_query_as_dict


def get_user_tweets(user_id):
    """
    Get a user's tweets ordered by created_at DESC.
    Use this function if you want to get tweets.
    Since the library neomodel doesn't support ordering by a property of Relationship,
    we should run a raw query.
    """
    query_params = {'user_pk': user_id}
    return cypher_query_as_dict(
        """MATCH (USER)-[written_tweets:WRITES_TWEET]->(TWEET)
WHERE USER.pk = {user_pk}
RETURN USER.pk as user_pk, USER.username as username, TWEET.pk as pk, TWEET.text as text,
    toInt(written_tweets.created_at * 1000) as created_at
ORDER BY written_tweets.created_at DESC""",
        params=query_params
    )
