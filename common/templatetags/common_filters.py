from django import template

from common.utils import timestamp2datetime

register = template.Library()

register.filter('timestamp2datetime', timestamp2datetime)
