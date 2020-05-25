# person.py
#
# Part of kepi.
# Copyright (c) 2018-2020 Marnanel Thurman.
# Licensed under the GNU Public License v2.

from polymorphic.models import PolymorphicModel
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import kepi.bowler_pub.crypto as crypto
from kepi.bowler_pub.utils import uri_to_url
import kepi.trilby_api.utils as trilby_utils
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import logging

logger = logging.Logger('kepi')

class Person(PolymorphicModel):

    @property
    def icon_or_default(self):
        if self.icon_image:
            return uri_to_url(self.icon_image)

        which = self.id % 10
        return uri_to_url('/static/defaults/avatar_{}.jpg'.format(
            which,
            ))

    @property
    def header_or_default(self):
        if self.header_image:
            return uri_to_url(self.header_image)

        return uri_to_url('/static/defaults/header.jpg')

    display_name = models.CharField(
            max_length = 255,
            verbose_name='display name',
            help_text = 'Your name, in human-friendly form. '+\
                'Something like "Alice Liddell".',
            )

    publicKey = models.TextField(
            blank=True,
            null=True,
            verbose_name='public key',
            )

    note = models.TextField(
            max_length=255,
            help_text="Your biography. Something like "+\
                    '"I enjoy falling down rabbitholes."',
            default='',
            verbose_name='bio',
            )

    auto_follow = models.BooleanField(
            default=True,
            help_text="If True, follow requests will be accepted automatically.",
            )

    locked = models.BooleanField(
            default=False,
            help_text="If True, only followers can see this account's statuses.",
            )

    bot = models.BooleanField(
            default=False,
            help_text="If True, this account is a bot. If False, it's a human.",
            )

    moved_to = models.URLField(
            max_length = 255,
            null = True,
            blank = True,
            default = True,
            help_text="If set, the account has moved away, and "+\
                    "this is where it went."
            )

    @property
    def uri(self):
        # I know this property is called "uri", but
        # this matches the behaviour of Mastodon
        return self.url

    @property
    def followers(self):
        # FIXME how should this work for remote?
        return Person.objects.filter(
            rel_following__following = self,
            )

    @property
    def following(self):
        # FIXME how should this work for remote?
        return Person.objects.filter(
            rel_followers__follower = self,
            )

    @property
    def fields(self):
        return [] # FIXME

    @property
    def emojis(self):
        return [] # FIXME

########################################

class RemotePerson(Person):

    url = models.URLField(
            max_length = 255,
            unique = True,
            null = True,
            blank = True,
            )

    status = models.IntegerField(
            default = 0,
            choices = [
                (0, 'pending'),
                (200, 'found'),
                (404, 'not found'),
                (410, 'gone'),
                (500, 'remote error'),
                ],
            )

    found_at = models.DateTimeField(
            null = True,
            default = None,
            )

    username = models.CharField(
            max_length = 255,
            null = True,
            blank = True,
            )

    inbox = models.URLField(
            max_length = 255,
            null = True,
            blank = True,
            default = None,
            )

    icon = models.URLField(
            max_length = 255,
            null = True,
            blank = True,
            default = None,
            )

    header = models.URLField(
            max_length = 255,
            null = True,
            blank = True,
            default = None,
            )

    key_name = models.CharField(
            max_length = 255,
            null = True,
            blank = True,
            default = '',
            )

    acct = models.CharField(
            max_length = 255,
            null = True,
            blank = True,
            default = None,
            unique = True,
            )

    created_at = models.DateTimeField(
            null = True,
            default = None,
            )

    icon_image = models.ImageField(
            help_text="A small square image used to identify you.",
            null=True,
            verbose_name='icon',
            blank = True,
            )

    header_image = models.ImageField(
            help_text="A large image, wider than it's tall, which appears "+\
                    "at the top of your profile page.",
            null=True,
            verbose_name='header image',
            blank = True,
            )

    @property
    def is_local(self):
        return False

    def __str__(self):
        if self.url is not None:
            return f'[{self.url}]'
        elif self.acct is not None:
            return f'[{self.acct}]'
        else:
            return '[<empty>]'

    @property
    def hostname(self):
        if self.url is not None:
            return urlparse(self.url).netloc

        if self.acct is not None:
            parts = self.acct.split('@')

            if parts[0]=='':
                # the format was @user@hostname
                parts.pop(0)

            return parts[1]

        return None

########################################

class TrilbyUser(AbstractUser):
    """
    A Django user.
    """
    pass

class LocalPerson(Person):

    local_user = models.OneToOneField(
            to = TrilbyUser,
            on_delete = models.CASCADE,
            null = True,
            blank = True,
            )

    created_at = models.DateTimeField(
            default = now,
            )

    privateKey = models.TextField(
            blank=True,
            null=True,
            verbose_name='private key',
            )

    icon_image = models.ImageField(
            help_text="A small square image used to identify you.",
            null=True,
            verbose_name='icon',
            blank = True,
            )

    header_image = models.ImageField(
            help_text="A large image, wider than it's tall, which appears "+\
                    "at the top of your profile page.",
            null=True,
            verbose_name='header image',
            blank = True,
            )

    def _generate_keys(self):

        logger.info('%s: generating key pair.',
                self.url)

        key = crypto.Key()
        self.privateKey = key.private_as_pem()
        self.publicKey = key.public_as_pem()

    def __init__(self, *args, **kwargs):

        if 'username' in kwargs and 'local_user' not in kwargs:
            new_user = TrilbyUser(
                    username=kwargs['username'])
            new_user.save()

            kwargs['local_user'] = new_user
            del kwargs['username']

            logger.info('created new TrilbyUser: %s',
                new_user)

        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        
        # Various defaults.

        if self.display_name=='':
            self.display_name = self.username

        # Create keys, if we're local and we don't have them.

        if self.privateKey is None and self.publicKey is None:
            self._generate_keys()

        # All good.

        super().save(*args, **kwargs)

    @property
    def username(self):
        return self.local_user.username

    @username.setter
    def username(self, newname):
        self.local_user.username = newname
        self.local_user.save()

    @property
    def is_local(self):
        return True

    @property
    def acct(self):
        return self.local_user.username

    def __str__(self):
        return self.username

    @property
    def url(self):
        return uri_to_url(settings.KEPI['USER_LINK'] % {
                'username': self.local_user.username,
                })

    @property
    def following_count(self):

        import kepi.trilby_api.models as trilby_models

        return trilby_models.Follow.objects.filter(
                follower = self,
                requested = False,
                ).count()

    @property
    def followers_count(self):

        import kepi.trilby_api.models as trilby_models

        return trilby_models.Follow.objects.filter(
                following = self,
                requested = False,
                ).count()

    @property
    def statuses_count(self):

        import kepi.trilby_api.models as trilby_models

        # TODO: not yet tested
        return trilby_models.Status.objects.filter(
                account = self,
                ).count()

    @property
    def key_name(self):
        return self.url + '#main-key'
