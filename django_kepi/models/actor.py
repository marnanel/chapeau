from django.db import models
from django.conf import settings
from . import acobject
import django_kepi.crypto
import logging
import json

logger = logging.getLogger(name='django_kepi')

LIST_NAMES = [
'inbox', 'outbox', 'followers', 'following',
]

######################

class AcActor(acobject.AcObject):
    """
    An AcActor is a kind of AcObject representing a person,
    an organisation, a bot, or anything else that can
    post stuff and interact with other AcActors.
    """

    privateKey = models.TextField(
            blank=True,
            null=True,
            )

    f_publicKey = models.TextField(
            blank=True,
            null=True,
            verbose_name='public key',
            )

    auto_follow = models.BooleanField(
            default=True,
            help_text="If True, follow requests will be accepted automatically.",
            )

    f_preferredUsername = models.CharField(
            max_length=255,
            help_text="Something short, like 'alice'.",
            verbose_name='username',
            )

    f_summary = models.TextField(
            max_length=255,
            help_text="Your biography. Something like "+\
                    "'I enjoy falling down rabbitholes.'",
            default='',
            verbose_name='bio',
            )

    icon = models.ImageField(
            help_text="A small square image used to identify you.",
            null=True,
            verbose_name='icon',
            )

    header = models.ImageField(
            help_text="A large image, wider than it's tall, which appears "+\
                    "at the top of your profile page.",
            null=True,
            verbose_name='header image',
            )

    @property
    def short_id(self):
        if self.is_local:
            return '@{}'.format(self.f_preferredUsername)
        else:
            return __super__.short_id

    @property
    def url(self):
        if self.is_local:
            return settings.KEPI['USER_URL_FORMAT'] % {
                    'username': self.f_preferredUsername,
                    'hostname': settings.KEPI['LOCAL_OBJECT_HOSTNAME'],
                    }
        else:
            return self.id

    def _after_create(self):
        if self.privateKey is None and self.f_publicKey is None:

            if not self.is_local:
                logger.warn('%s: Attempt to save remote without key',
                        self.url)
            else:
                logger.info('%s: generating key pair.',
                        self.url)

                key = django_kepi.crypto.Key()
                self.privateKey = key.private_as_pem()
                self.f_publicKey = key.public_as_pem()

    def __str__(self):
        if self.is_local:
            return '({}) @{}'.format(
                    self.id,
                    self.f_preferredUsername,
                    )
        else:
            return '({}) [remote user]'.format(
                    self.id,
                    )

    @property
    def key_name(self):
        """
        The name of this key.
        """
        return '%s#main-key' % (self.url,)

    def list_url(self, name):
        return settings.KEPI['COLLECTION_URL'] % {
                'hostname': settings.KEPI['LOCAL_OBJECT_HOSTNAME'],
                'username': self.f_preferredUsername,
                'listname': name,
                }

    def __setitem__(self, name, value):
        if name=='privateKey':
            self.privateKey = value
            logger.info('%s: setting private key to %s',
                    self, self.privateKey)
            self.save()
        elif name=='publicKey':
            self.f_publicKey = json.dumps(value,
                    sort_keys = True)
            logger.info('%s: setting public key to %s',
                    self, self.f_publicKey)
            self.save()
        else:
            super().__setitem__(name, value)

    def __getitem__(self, name):
        if self.is_local:

            if name in LIST_NAMES:
                return self.list_url(name)
            elif name=='privateKey':
                return self.privateKey

        if name=='publicKey':
            if not self.f_publicKey:
                logger.debug('%s: we have no known public key',
                        self)
                return None

            result = json.loads(self.f_publicKey)
            logger.debug('%s: public key is %s',
                    self, result)
            return result

        return super().__getitem__(name)

    @property
    def activity_form(self):
        result = super().activity_form

        if 'publicKey' in result:
            result['publicKey'] = {
                'id': self.id + '#main-key',
                'owner': self.id,
                'publicKeyPem': result['publicKey'],
                }

        for listname in LIST_NAMES:
            result[listname] = self.list_url(listname)

        result['url'] = self.url
        result['name'] = self.f_preferredUsername

        result['endpoints'] = {}
        if 'SHARED_INBOX' in settings.KEPI:
            result['endpoints']['sharedInbox'] = \
                    settings.KEPI['SHARED_INBOX'] % {
           'hostname': settings.KEPI['LOCAL_OBJECT_HOSTNAME'],
                            }

        result['tags'] = []
        result['attachment'] = []

        result['summary'] = '(Kepi user)'

        # default images, for now
        result['icon'] = {
                "type":"Image",
                "mediaType":"image/jpeg",
                "url": 'https://%(hostname)s/static/defaults/avatar_0.jpg' % {
                    'hostname': settings.KEPI['LOCAL_OBJECT_HOSTNAME'],
                    },
                }

        result['header'] = {
                "type":"Image",
                "mediaType":"image/jpeg",
                "url": 'https://%(hostname)s/static/defaults/header.jpg' % {
                    'hostname': settings.KEPI['LOCAL_OBJECT_HOSTNAME'],
                    },
                }

        return result

##############################

class AcApplication(AcActor):
    pass

class AcGroup(AcActor):
    pass

class AcOrganization(AcActor):
    pass

class AcPerson(AcActor):
    class Meta:
        verbose_name = 'person'
        verbose_name_plural = 'people'

class AcService(AcActor):
    pass
