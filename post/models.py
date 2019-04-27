import uuid
from enum import Enum

from django.db import models

from accounts.models import User


class ScoringHistoryType(Enum):
    """Enum that describes types of Scoring History."""
    POST_WRITE = 'POST_WRITE'
    POST_LIKE = 'POST_LIKE'
    POST_COMMENT = 'POST_COMMENT'


class ScoringHistory(models.Model):
    """Model that records Scoring History."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tweet_id = models.UUIDField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    delta_score = models.FloatField()
    cumulative_score = models.FloatField()

    type = models.CharField(
        max_length=32,
        choices=((t, t.value) for t in ScoringHistoryType)
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
