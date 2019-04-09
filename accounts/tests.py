import json
import logging

import neomodel
from django.test import TestCase, Client
from django.urls import reverse
from neomodel import db as graphdb

from accounts.models import User

APPLICATION_JSON = 'application/json'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)


class AccountTest(TestCase):
    setup_done = False
    username = 'sinwoobang'
    password = '1234!@#$'
    email = 'sinwoobang@gmail.com'

    def setUp(self):
        """Setup to initialize data. It is called before each test method is called."""
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logger.info("Clearing Graph...")
        neomodel.clear_neo4j_database(graphdb)
        neomodel.install_all_labels()

        logger.info("Creating a user...")
        User.objects.create_user(username=cls.username, password=cls.password)

    def test_api_register(self):
        """Test for accounts.apis.register"""
        url_ = reverse('account.api.register')
        raw_data = {
            'username': self.username+'2',
            'password1': self.password,
            'password2': self.password,
            'email': self.email
        }
        data = json.dumps(raw_data)
        res = self.client.post(path=url_, data=data, content_type=APPLICATION_JSON)
        self.assertIn('success', str(res.content))

    def test_api_login(self):
        """Test for accounts.apis.register"""
        url = reverse('account.api.login')
        raw_data = {
            'username': self.username,
            'password': self.password
        }
        data = json.dumps(raw_data)
        res = self.client.post(path=url, data=data, content_type=APPLICATION_JSON)
        self.assertIn('success', str(res.content))
