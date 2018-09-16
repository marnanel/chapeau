from django.db import models
from django_kepi import register_type, TombstoneException
from django_kepi import models as kepi_models

class ThingUser(models.Model):

    name = models.CharField(max_length=256)

    favourite_colour = models.CharField(
            max_length=256,
            default='chartreuse',
            )

    def __str__(self):
        return '[ThingUser {}]'.format(self.name)

    @property
    def activity(self):

        if self.name=='Queen Anne':
            raise TombstoneException(original_type=self.activity_type)

        return {
                'id': self.activity_id,
                'type': self.activity_type,
                'name': self.name,
                'favourite_colour': self.favourite_colour,
                }

    @property
    def activity_type(self):
        return 'Person'

    @property
    def activity_id(self):
        return 'https://example.com/user/{}'.format(
                self.name,
                )

    @classmethod
    def find_activity(cls, url):
        PREFIX = "https://example.com/user/"
        if not url.startswith(PREFIX):
            return None

        name = url[len(PREFIX):]

        return cls.objects.get(name=name)

register_type('Person', ThingUser)

class ThingArticle(models.Model):

    title = models.CharField(max_length=256)
    ftype = 'Article'

    def serialize(self):
        return {
                'id': self.url_identifier(),
                'type': 'Article',
                'title': self.title,
                }
        
    def url_identifier(self):
        return 'https://articles.example.com/{}'.format(
                self.title,
                )

    @classmethod
    def activity_create(cls, type_name, actor, fields):
        pass

    @classmethod
    def activity_update(cls, type_name, actor, fields, partial):
        pass

    @classmethod
    def activity_delete(cls, type_name, actor):
        pass

    @classmethod
    def activity_like(cls, type_name, actor, fobject):
        pass

    @classmethod
    def find_activity(cls, url):
        PREFIX = "https://articles.example.com/"
        if not url.startswith(PREFIX):
            return None

        title = url[len(PREFIX):]

        return cls.objects.get(title=title)

register_type('Article', ThingArticle)

