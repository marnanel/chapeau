from django.test import TestCase, Client
from rest_framework.test import force_authenticate, APIClient
from kepi.trilby_api.models import *
from django.conf import settings

ACCOUNT_EXPECTED = [
        ('id', '@alice'),
        ('username', 'alice'),
        ('acct', 'alice@testserver'),
        ('display_name', 'alice'),
        ('locked', False),

        ('followers_count', 0),
        ('following_count', 0),
        ('statuses_count', 0),
        ('note', ''),
        ('url', 'https://testserver/users/alice'),
        ('fields', []),
        ('emojis', []),

        ('avatar', 'https://testserver/static/defaults/avatar_1.jpg'),
        ('header', 'https://testserver/static/defaults/header.jpg'),
        ('avatar_static', 'https://testserver/static/defaults/avatar_1.jpg'),
        ('header_static', 'https://testserver/static/defaults/header.jpg'),

        ('bot', False),
        ]

ACCOUNT_SOURCE_EXPECTED = [
        ('privacy', 'A'),
        ('sensitive', False),
        ('language', settings.KEPI['LANGUAGES'][0]), # FIXME
        ]

STATUS_EXPECTED = [
        ('in_reply_to_account_id', None),
        ('content', 'Hello world.'),
        ('emojis', []),
        ('reblogs_count', 0),
        ('favourites_count', 0),
        ('reblogged', False),
        ('favourited', False),
        ('muted', False),
        ('sensitive', False),
        ('spoiler_text', ''),
        ('visibility', 'A'),
        ('media_attachments', []),
        ('mentions', []),
        ('tags', []),
        ('card', None),
        ('poll', None),
        ('application', None),
        ('language', 'en'),
        ('pinned', False),
        ]

class TrilbyTestCase(TestCase):

    def setUp(self):

        settings.KEPI['LOCAL_OBJECT_HOSTNAME'] = 'testserver'

        super().setUp()

    def _create_alice(self):

        # TODO: this should be replaced with a general-case "_create_user()"
        # that then gets used everywhere

        result = create_local_person('alice')
        self._alice = result
        return result

    def request(self, verb, path,
            data={},
            as_user=None,
            *args, **kwargs,
            ):

        c = APIClient()

        if as_user:
            c.force_authenticate(as_user.local_user)

        command = getattr(c, verb)

        result = command(
                path=path,
                data=data,
                format='json',
                *args,
                **kwargs,
                )

        return result

    def get(self, *args, **kwargs):
        return self.request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('post', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request('patch', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request('delete', *args, **kwargs)

def create_local_person(name='jemima'):

    result = Person(
            username = name,
            )
    result.save()

    return result

def create_local_status(content,
        posted_by,
        **kwargs,
        ):

    if isinstance(posted_by, TrilbyUser):
        posted_by = posted_by.person

    result = Status(
        remote_url = None,
        account = posted_by,
        content = content,
        **kwargs,
        )

    result.save()

    return result

def _client_request(
        path, data,
        as_user,
        is_post,
        ):

    c = APIClient()

    if as_user is not None:

        if isinstance(as_user, Person):
            as_user = as_user.local_user

        c.force_authenticate(as_user)

    if is_post:
        result = c.post(
                path,
                data,
                format = 'json',
                )
    else:
        result = c.get(
                path,
                format = 'json',
                )

    return result

def post(path,
        data,
        as_user = None):

    return _client_request(path, data, as_user,
            is_post = True)

def get(path,
        as_user = None):

    return _client_request(path, {}, as_user,
            is_post = False)

