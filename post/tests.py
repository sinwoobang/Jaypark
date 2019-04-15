import json
import logging

import neomodel
from django.test import TestCase, Client
from django.urls import reverse
from neomodel import db as graphdb

from accounts.models import User
from accounts.graphs import User as UserNode
from feed.graphs import Tweet
from common.utils import extract_hashtags
from post.graphs import Comment as CommentNode

APPLICATION_JSON = 'application/json'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)


class PostTest(TestCase):
    username = 'sinwoobang'
    password = '1234!@#$'
    email = 'sinwoobang@gmail.com'

    def setUp(self):
        """Setup to initialize data"""
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logger.info("Clearing Graph...")
        neomodel.clear_neo4j_database(graphdb)
        neomodel.install_all_labels()

        logger.info("Creating a user...")
        User.objects.create_user(username=cls.username, password=cls.password)
        
    def test_api_write(self):
        """Test for post.apis.write"""
        logger.info("Testing api_write...")
        url = reverse('post.api.write')

        text = 'Hi there!'
        raw_data = {'text': text}
        data = json.dumps(raw_data)
        res = self.client.post(path=url, data=data, content_type=APPLICATION_JSON)

        tweet_node = Tweet.nodes.get_or_none()
        self.assertIsNotNone(tweet_node, res.content)

        """Test writing which contains HashTag"""
        text = 'Hi there!#asdf'
        raw_data = {'text': text}
        data = json.dumps(raw_data)
        res = self.client.post(path=url, data=data, content_type=APPLICATION_JSON)
        res_content = json.loads(res.content)
        tweet_id = res_content['contents']['tweet']['id']

        tweet_node = Tweet.nodes.get_or_none(pk=tweet_id)
        self.assertIsNotNone(tweet_node, res.content)

        """Check whether a tag and a tweet are connected"""
        tag = list(extract_hashtags(text))[0]
        tag_node = tweet_node.tags.get_or_none(tag=tag)
        self.assertIsNotNone(tag_node, res.content)

    def test_api_write_and_like_comment(self):
        """Test for post.apis.write_comment and post.apis.like_comment"""
        logger.info("Testing api_write_comment...")

        """Write a tweet before testing a comment."""
        logger.info("Writing a tweet to test...")
        url = reverse('post.api.write')

        text = 'Hi there!'
        raw_data = {'text': text}
        data = json.dumps(raw_data)
        res = self.client.post(path=url, data=data, content_type=APPLICATION_JSON)
        res_content = json.loads(res.content)
        tweet_id = res_content['contents']['tweet']['id']

        """Start testing"""
        url = reverse('post.api.write_comment')

        text = 'Hi This is Comment!'
        raw_data = {'text': text, 'tweet_id': tweet_id}
        data = json.dumps(raw_data)
        res = self.client.post(path=url, data=data, content_type=APPLICATION_JSON)
        res_content = json.loads(res.content)
        self.assertIn('contents', res_content, res_content)
        comment_id = res_content['contents']['comment']['id']

        comment_node = CommentNode.nodes.get_or_none(pk=comment_id)
        self.assertIsNotNone(comment_node, res_content)

        user_node = UserNode.nodes.get(username=self.username)
        is_user_connected = user_node.comments_written.is_connected(comment_node)
        self.assertTrue(is_user_connected, 'User not connected.')

        tweet_node = Tweet.nodes.get(pk=tweet_id)
        is_tweet_connected = tweet_node.comments_written.is_connected(comment_node)
        self.assertTrue(is_tweet_connected, 'Tweet not connected.')

        logger.info("Testing api_like_comment...")
        url = reverse('post.api.like_comment')
        raw_data = {'comment_id': comment_id}
        data = json.dumps(raw_data)
        self.client.post(path=url, data=data, content_type=APPLICATION_JSON)

        is_user_connected = user_node.comments_liked.is_connected(comment_node)
        self.assertTrue(is_user_connected, res.content)

        logger.info("Testing api_unlike_comment...")
        url = reverse('post.api.unlike_comment')
        raw_data = {'comment_id': comment_id}
        data = json.dumps(raw_data)
        self.client.post(path=url, data=data, content_type=APPLICATION_JSON)

        is_user_connected = user_node.comments_liked.is_connected(comment_node)
        self.assertFalse(is_user_connected, res.content)
