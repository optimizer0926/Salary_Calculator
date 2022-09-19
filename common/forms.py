# coding:utf-8
from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from common.models import Establishment


class CleanStartEndMixin(object):
    def clean(self):
        data = super(CleanStartEndMixin, self).clean()
        if data.get('start_date') > data.get('end_date'):
            self.add_error(
                'end_date', ValidationError(
                    _(u'Дата окончания должна быть позже даты начала.')
                )
            )
