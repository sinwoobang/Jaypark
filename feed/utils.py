from common.utils.etc import cypher_query_as_dict


def get_user_tweets(user_id, order_by=None):
    """
    Get a user's tweets ordered by created_at DESC.
    Use this function if you want to get tweets.
    Since the library neomodel doesn't support ordering by a property of Relationship,
    we should run a raw query.
    """
    query_params = {'user_pk': user_id}

    query = """MATCH (USER {pk:{user_pk}})-[w:WRITES_TWEET]->(TWEET)
        OPTIONAL MATCH (USER)-[l:LIKES_TWEET]->(TWEET)
        RETURN USER.pk as user_pk, USER.username as username, TWEET.pk as pk, TWEET.text as text,
            TWEET.score as score,
            toInt(w.created_at * 1000) as created_at, l IS NOT NULL as is_liked
        """

    query_order_by = 'ORDER BY {0} DESC'
    if order_by:
        if order_by == 'created_at':
            query_order_by = query_order_by.format('created_at')
        elif order_by == 'score':
            query_order_by = query_order_by.format('score')
        else:
            raise ValueError(f'The property {order_by} does not exist.')
        query += query_order_by

    return cypher_query_as_dict(query, params=query_params)
