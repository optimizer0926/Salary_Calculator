# coding: utf-8
from django import forms
from django.utils.translation import ugettext as _

from common.mixins import CleanMonthYearMixin
from personnel.models import Department


class ReportForm(CleanMonthYearMixin, forms.Form):
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.filter(active=True),
        widget=forms.SelectMultiple(attrs={
            'data-role': 'multiselect',
            'data-button-width': '100%',
            'data-inherit-class': 'true',
            'data-non-selected-text': _(u'Выберете отделы'),
            'data-n-selected-text': _(u'выбрано'),
            'data-all-selected-text': _(u'Все отделы'),
            'data-include-select-all-option': 'true',
            'data-select-all-text': _(u'Все отделы'),
        }),
        label=_(u'Отделы'),
    )
    month_year = forms.CharField(
        widget=forms.DateInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'mm/yyyy',
                'data-date-language': 'ru',
                'data-date-min-view-mode': 'months',
        }, format=('%m/%Y')),
        label=_(u'За месяц'),
    )

    class Media:
        css = {
            'all': (
                'assets/css/bootstrap-datepicker3.min.css',
                'assets/css/bootstrap-multiselect.css',
            ),
        }
        js = (
            'assets/js/bootstrap-datepicker.min.js',
            'assets/locales/bootstrap-datepicker.ru.min.js',
            'assets/js/bootstrap-multiselect.js',
        )

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['departments'].help_text = _(u'Выберете один или несколько отделов')
