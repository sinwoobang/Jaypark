import json
import logging

import neomodel
from django.test import TestCase, Client
from django.urls import reverse
from neomodel import db as graphdb

from accounts.graphs import Tweet

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
        neomodel.clear_neo4j_database(graphdb)
        neomodel.install_all_labels()

        # register a user via API to prevent to be fragmented
        url_register = reverse('account.api.register')
        raw_data_register = {
            'username': self.username,
            'password1': self.password,
            'password2': self.password,
            'email': self.email
        }
        data_register = json.dumps(raw_data_register)
        self.client.post(path=url_register, data=data_register, content_type=APPLICATION_JSON)
        
    def test_api_write(self):
        """Test for post.apis.write"""
        url = reverse('post.api.write')
        text = 'Hi there!'
        raw_data = {'text': text}
        data = json.dumps(raw_data)
        res = self.client.post(path=url, data=data, content_type=APPLICATION_JSON)

        tweet = Tweet.nodes.get_or_none()
        self.assertIsNotNone(tweet, res.content)
