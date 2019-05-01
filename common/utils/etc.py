import re
import socket
from datetime import datetime

from dateutil.tz import tzutc
from django.conf import settings
from neomodel import db as graphdb


def cypher_query_as_dict(query, params):
    """
    Run a cypher query and change its type from List to Dictionary.
    :param query: Cypher Query
    :param params: Parameters of the query
    :return: A list whose type of each element is Dictionary.
    """
    query_result = graphdb.cypher_query(query, params=params)
    data_raw = query_result[0]  # The result data of the query
    field_names = query_result[1]

    data = []  # a return data
    for row in data_raw:  # iterates a raw data and changes its type to Dict.
        element = {}
        for idx, field_name in enumerate(field_names):
            element[field_name] = row[idx]
        data.append(element)
    return data


def timestamp2datetime(timestamp):
    """
    Convert Timestamp to Datetime
    :param timestamp:
        Timestamp(ex. 1554908239776).
        Please NOTE you should multiply * 1000 if you've used the default timestamp in Python.
    :return Datetime object:
    :rtype: datetime.datetime
    """
    return datetime.utcfromtimestamp(timestamp // 1000)


def datetime2timestamp(dt, default_timezone=None):
    """Calculate the timestamp based on the given datetime instance.

    :type dt: datetime
    :param dt: A datetime object to be converted into timestamp
    :type default_timezone: tzinfo
    :param default_timezone: If it is provided as None, we treat it as tzutc().
                             But it is only used when dt is a naive datetime.
    :returns: The timestamp
    """
    epoch = datetime(1970, 1, 1)
    if dt.tzinfo is None:
        if default_timezone is None:
            default_timezone = tzutc()
        dt = dt.replace(tzinfo=default_timezone)
    d = dt.replace(tzinfo=None) - dt.utcoffset() - epoch
    if hasattr(d, "total_seconds"):
        return int(d.total_seconds())  # Works in Python 2.7+
    return int((d.microseconds + (d.seconds + d.days * 24 * 3600) * 10**6) / 10**9)


def username2url(username):
    """Return a url which redirects to a users' feed."""
    return f'{get_current_host_url()}/{username}'


def extract_hashtags(text):
    """
    Extract hashtags in the text
    Original Post : https://stackoverflow.com/questions/2527892/
    :param text: ex. "I love #stackoverflow because #people are very #helpful!"
    :type text: str
    :return: ex. {'#stackoverflow', '#people', '#helpful!'}
    :rtype: set
    """
    return set(re.findall(r"#(\w+)", text))


def is_local():
    """Check whether it is local PC or not."""
    return 'sinwoo' in socket.gethostname()


def get_current_host_url():
    """Get the host url based on the current server status"""
    if settings.DEBUG or is_local():
        return 'http://jaypark.sinwoobang.me:8000'
    return 'http://jaypark.sinwoobang.me'


def get_human_number(num):
    """Get Human Readable Format of the number."""
    if num < 1000:
        return num

    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
