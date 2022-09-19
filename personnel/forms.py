# coding:utf-8
from decimal import Decimal

from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from personnel.models import (
    Department,
    Employee,
    Position,
    Bonus,
    SickTime,
    Vacation,
)
from common.mixins import CleanMonthYearMixin
from common.forms import CleanStartEndMixin


class PersonnelForm(ModelForm):
    class Meta:
        exclude = (
            'active',
            'created_date',
            'updated_date',
            'created_by',
            'updated_by',
        )

    class Media:
        js = (
            'assets/js/bootstrap-inputmask/bootstrap-inputmask.min.js',
            'assets/js/form-component.js',
        )


class DepartmentForm(PersonnelForm):
    class Meta(PersonnelForm.Meta):
        model = Department
        labels = {
            'name': _(u'Название отдела'),
        }


class EmployeeForm(PersonnelForm):
    hired = forms.DateField(
        widget=forms.DateInput(attrs={
                'data-provide': 'datepicker',
                'data-date-language': 'ru',
                'data-date-format': 'dd.mm.yyyy',
        }),
        label=_(u'Дата приема на работу'),
    )

    class Meta(PersonnelForm.Meta):
        model = Employee
        labels = {
            'name': _(u'Фамилия, Имя, Отчество'),
            'department': _(u'Отдел'),
            'position': _(u'Должность'),
            'personnel_number': _(u'Табельный номер'),
            'permanent_bonus_amount': _(u'Постоянная премия'),
            'insurance_experience': _(u'Страховой стаж'),
        }

    class Media:
        css = {
            'all': ('assets/css/bootstrap-datepicker3.min.css',),
        }
        js = (
            'assets/js/bootstrap-datepicker.min.js',
            'assets/locales/bootstrap-datepicker.ru.min.js',
        )


class PositionForm(PersonnelForm):
    class Meta(PersonnelForm.Meta):
        model = Position
        labels = {
            'name': _(u'Название'),
            'wages': _(u'Ставка'),
        }


class BonusForm(CleanMonthYearMixin, PersonnelForm):
    percent = forms.FloatField(
        required=False,
        min_value=0,
        label=_(u'Процент от заработной платы'),
        help_text=_(u'Введите процентное соотношение размера премии к заработной плате '
            u'сотрудника.'),
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

    class Meta(PersonnelForm.Meta):
        model = Bonus
        fields = (
            'employee',
            'month_year',
            'percent',
            'amount',
            'description',
        )
        labels = {
            'amount': _(u'Сумма'),
            'description': _(u'Описание'),
        }

    class Media:
        css = {
            'all': ('assets/css/bootstrap-datepicker3.min.css',),
        }
        js = (
            'assets/js/bootstrap-datepicker.min.js',
            'assets/locales/bootstrap-datepicker.ru.min.js',
        )

    def __init__(self, *args, **kwargs):
        super(BonusForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['month_year'] = "{month:0>2d}/{year}".format(
                month=self.instance.month,
                year=self.instance.year
            )

    def save(self, commit=True):
        instance = super(BonusForm, self).save(commit=False)
        instance.month, instance.year = self.cleaned_data['month_year']
        if commit:
            instance.save()
        return instance


class BonusCreateForm(BonusForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(active=True),
        label=_(u'Сотрудник'),
    )

    class Meta(BonusForm.Meta):
        exclude = (
            'amount',
        )

    def save(self, commit=True):
        instance = super(BonusCreateForm, self).save(commit=False)
        instance.amount = instance.employee.wages * Decimal(self.cleaned_data['percent'] / 100.0)
        if commit:
            instance.save()
        return instance


class BonusUpdateForm(BonusForm):
    class Meta(BonusForm.Meta):
        exclude = BonusForm.Meta.exclude + (
            'employee',
        )


class SickTimeForm(CleanStartEndMixin, PersonnelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
                'data-provide': 'datepicker',
                'data-date-language': 'ru',
                'data-date-format': 'dd.mm.yyyy',
        }),
        label=_(u'Начало'),
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
                'data-provide': 'datepicker',
                'data-date-language': 'ru',
                'data-date-format': 'dd.mm.yyyy',
        }),
        label=_(u'Окончание'),
    )

    class Meta(PersonnelForm.Meta):
        model = SickTime
        labels = {
            'last_two_years_wages': _(u'Суммарный заработок за последние 24 месяца'),
        }
        help_texts = {
            'last_two_years_wages': _(u'Укажите фактический суммарный ежемесячный заработок сотрудника '
                u'за последние 24 месяца. Необходимы все выплаты, на которые начислены страховые взносы в ФСС. '
                u'К таким выплатам не относятся больничные, пособия за счет ФСС и другие выплаты '
                u'в соответствии со ст.9 212-ФЗ.'
            )
        }

    class Media:
        css = {
            'all': ('assets/css/bootstrap-datepicker3.min.css',),
        }
        js = (
            'assets/js/bootstrap-datepicker.min.js',
            'assets/locales/bootstrap-datepicker.ru.min.js',
        )


class SickTimeCreateForm(SickTimeForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(active=True),
        label=_(u'Сотрудник'),
    )


class SickTimeUpdateForm(SickTimeForm):
    class Meta(SickTimeForm.Meta):
        exclude = SickTimeForm.Meta.exclude + (
            'employee',
        )


class VacationForm(CleanStartEndMixin, PersonnelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
                'data-provide': 'datepicker',
                'data-date-language': 'ru',
                'data-date-format': 'dd.mm.yyyy',
        }),
        label=_(u'Начало'),
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
                'data-provide': 'datepicker',
                'data-date-language': 'ru',
                'data-date-format': 'dd.mm.yyyy',
        }),
        label=_(u'Окончание'),
    )

    class Meta(PersonnelForm.Meta):
        model = Vacation
        labels = {
            'average_daily_earnings': _(u'Среднедневной заработок'),
        }
        help_texts = {
                'average_daily_earnings': _(u'Средний дневной заработок по всем начислениям за расчетный период '
                    u'кроме следующих: '
                    u'больничные, отпуска, пособия до полутора лет, оплата по среднему заработку, '
                    u'и др. начисления в соответствии с п.5 Постановления Правительства РФ №922 от 24.12.2007г.;'
                ),
        }

    class Media:
        css = {
            'all': ('assets/css/bootstrap-datepicker3.min.css',),
        }
        js = (
            'assets/js/bootstrap-datepicker.min.js',
            'assets/locales/bootstrap-datepicker.ru.min.js',
        )


class VacationCreateForm(VacationForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(active=True),
        label=_(u'Сотрудник'),
    )


class VacationUpdateForm(VacationForm):
    class Meta(VacationForm.Meta):
        exclude = VacationForm.Meta.exclude + (
            'employee',
        )
