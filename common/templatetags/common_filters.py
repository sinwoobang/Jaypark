from django import template

from common.utils import timestamp2datetime, username2url

register = template.Library()

register.filter('timestamp2datetime', timestamp2datetime)
register.filter('username2url', username2url)
