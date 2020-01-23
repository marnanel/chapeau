from django.test import TestCase
from rest_framework.test import force_authenticate, APIClient, APIRequestFactory
from kepi.trilby_api.views import *
from kepi.trilby_api.tests import *
from kepi.bowler_pub.tests import *
from django.conf import settings
import logging
import httpretty

logger = logging.getLogger(name='kepi')

DEFAULT_KEYS_FILENAME = 'kepi/bowler_pub/tests/keys/keys-0002.json'
TESTSERVER = 'testserver'

class TestNotifications(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        settings.KEPI['LOCAL_OBJECT_HOSTNAME'] = TESTSERVER

    @httpretty.activate
    def test_follow(self):
        alice = create_local_trilbyuser(name='alice')

        fred_keys = json.load(open(DEFAULT_KEYS_FILENAME, 'r'))

        fred = create_remote_person(
                name='fred',
                publicKey = fred_keys['public'],
                url=REMOTE_FRED,
                )

        post_test_message(
                secret = fred_keys['private'],
                host = TESTSERVER,
                f_type = 'Follow',
                f_actor = REMOTE_FRED,
                f_object = alice.actor.url,
                )

        request = self.factory.get(
                '/api/v1/notifications/',
                )
        force_authenticate(request, user=alice)

        view = Notifications.as_view()
        result = view(request)
        result.render()

        self.assertEqual(
                result.status_code,
                200,
                msg = result.content,
                )

        content = json.loads(result.content.decode())

        self.assertEqual(
                len(content),
                1,
                )

        self.assertDictContainsSubset(
                {
                    'type': 'follow',
                    },
                content[0],
                )

        self.assertIn(
                'account',
                content[0],
                )

        self.assertDictContainsSubset(
                {
                    'id': 'https://remote.example.org/users/fred',
                    'username': 'fred',
                    'acct': 'fred@remote.example.org',
                    'url': 'https://remote.example.org/users/fred',
                    },
                content[0]['account'],
                )

    @httpretty.activate
    def test_favourite(self):
        alice = create_local_trilbyuser(name='alice')

        status_creation = create_local_status(
                content = 'Curiouser and curiouser!',
                posted_by = alice,
                )

        status = status_creation['object__obj']

        fred_keys = json.load(open(DEFAULT_KEYS_FILENAME, 'r'))

        fred = create_remote_person(
                name='fred',
                publicKey = fred_keys['public'],
                url=REMOTE_FRED,
                )

        post_test_message(
                secret = fred_keys['private'],
                host = TESTSERVER,
                f_type = 'Like',
                f_actor = REMOTE_FRED,
                f_object = status.url,
                )

        request = self.factory.get(
                '/api/v1/notifications/',
                )
        force_authenticate(request, user=alice)

        view = Notifications.as_view()
        result = view(request)
        result.render()

        self.assertEqual(
                result.status_code,
                200,
                msg = result.content,
                )

        content = json.loads(result.content.decode())

        self.assertEqual(
                len(content),
                1,
                )

        self.assertDictContainsSubset(
                {
                    'type': 'favourite',
                    },
                content[0],
                )

        self.assertIn(
                'account',
                content[0],
                )

        self.assertDictContainsSubset(
                {
                    'id': 'https://remote.example.org/users/fred',
                    'username': 'fred',
                    'acct': 'fred@remote.example.org',
                    'url': 'https://remote.example.org/users/fred',
                    },
                content[0]['account'],
                )

        self.assertIn(
                'status',
                content[0],
                )

        self.assertDictContainsSubset(
                {
                    'id': status.id[1:],
                    'content': '<p>Curiouser and curiouser!</p>',
                    },
                content[0]['status'],
                )
