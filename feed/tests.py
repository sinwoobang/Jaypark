from django.test import TestCase

from common.utils.etc import extract_hashtags


class FeedTest(TestCase):
    def test_utils_extract_hashtags(self):
        tags = extract_hashtags('#가나다#라마바#사아자 차카타')
        self.assertSetEqual(tags, {'가나다', '라마바', '사아자'})

        tags = extract_hashtags('#가나다#라마바#사아자###asdf 차카타')
        self.assertSetEqual(tags, {'가나다', '라마바', '사아자', 'asdf'})

        tags = extract_hashtags('#가나다#라마바#사아자###asdf(!@#) 차카타')
        self.assertSetEqual(tags, {'가나다', '라마바', '사아자', 'asdf'})
