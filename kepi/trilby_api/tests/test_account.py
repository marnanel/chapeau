from unittest import skip
from rest_framework.test import APIClient, force_authenticate
from kepi.trilby_api.views import *
from kepi.trilby_api.tests import *
from kepi.trilby_api.models import *
from django.conf import settings

# Tests for accounts. API docs are here:
# https://docs.joinmastodon.org/methods/accounts/

class TestAccountCredentials(TrilbyTestCase):

    # Getting the list of an account's statuses is handled in test_timeline.

    def test_verify_credentials_anonymous(self):
        result = self.get(
                '/api/v1/accounts/verify_credentials',
                )

        self.assertEqual(
                result.status_code,
                401,
                )

    def test_verify_credentials(self):
        self._user_test(
                name='verify_credentials',
                )

    def test_verify_user(self):
        self._user_test(
                name='alice',
                )

    def _user_test(self, name):
        alice = create_local_person(name='alice')

        result = self.get(
                '/api/v1/accounts/'+name,
                as_user = alice,
                )

        self.assertEqual(
                result.status_code,
                200,
                )

        content = json.loads(result.content)

        self.assertIn('created_at', content)
        self.assertNotIn('email', content)

        for field, expected in ACCOUNT_EXPECTED:
            self.assertIn(field, content)
            self.assertEqual(content[field], expected,
                    msg="field '{}'".format(field))

        self.assertIn('source', content)

        for field, expected in ACCOUNT_SOURCE_EXPECTED:
            self.assertIn(field, content['source'])
            self.assertEqual(content['source'][field], expected,
                    msg="field 'source.{}'".format(field))

    @skip("Not yet implemented")
    def test_register(self):
        pass
   
    @skip("Not yet implemented")
    def test_update_credentials(self):
        pass

    @skip("Not yet implemented")
    def test_get_account(self):
        pass

    @skip("Not yet implemented")
    def test_account_followers(self):
        pass

    @skip("Not yet implemented")
    def test_account_following(self):
        pass

    @skip("Not yet implemented")
    def test_account_in_lists(self):
        pass

    @skip("Not yet implemented")
    def test_account_relationships(self):
        pass

    @skip("Not yet implemented")
    def test_account_search(self):
        pass

class TestAccountActions(TrilbyTestCase):

    @skip("Not yet implemented")
    def test_follow(self):
        pass

    @skip("Not yet implemented")
    def test_unfollow(self):
        pass

    @skip("Not yet implemented")
    def test_block(self):
        pass

    @skip("Not yet implemented")
    def test_unblock(self):
        pass

    @skip("Not yet implemented")
    def test_mute(self):
        pass

    @skip("Not yet implemented")
    def test_unmute(self):
        pass

