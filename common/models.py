# coding:utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class CommonModel(models.Model):
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(to=User, related_name='+')
    updated_by = models.ForeignKey(to=User, related_name='+')

    class Meta:
        abstract = True


class UnicodeNameMixin(object):
    def __unicode__(self):
        return self.name


class Establishment(UnicodeNameMixin, models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _(u'организация')
        verbose_name_plural = _(u'организации')
