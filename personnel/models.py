# coding:utf-8
from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum

from common.models import CommonModel
from common.models import UnicodeNameMixin
from common.utils import business_days

ABSTRACT_RATIO = Decimal('730.00')
MINIMAL_DAILY_WAGES = Decimal('196.10')
MAXIMUM_DAILY_WAGES = Decimal('1632.87')

INSURANCE_EXPERIENCE_LESS_THAN_FIVE_YEARS = 0
INSURANCE_EXPERIENCE_FROM_FIVE_TO_EIGHT_YEARS = 1
INSURANCE_EXPERIENCE_MORE_THAN_EIGHT_YEARS = 2
INSURANCE_RATIO = {
    INSURANCE_EXPERIENCE_LESS_THAN_FIVE_YEARS: Decimal('0.60'),
    INSURANCE_EXPERIENCE_FROM_FIVE_TO_EIGHT_YEARS: Decimal('0.80'),
    INSURANCE_EXPERIENCE_MORE_THAN_EIGHT_YEARS: Decimal('1.00'),
}

TWOPLACES = Decimal(10) ** -2


class Department(UnicodeNameMixin, CommonModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _(u'отдел')
        verbose_name_plural = _(u'отделы')


class Position(UnicodeNameMixin, CommonModel):
    name = models.CharField(max_length=100)
    wages = models.DecimalField(max_digits=22, decimal_places=2)

    class Meta:
        verbose_name = _(u'должность')
        verbose_name_plural = _(u'должности')


class Employee(UnicodeNameMixin, CommonModel):
    INSURANCE_EXPERIENCE_CHOICES = (
        (INSURANCE_EXPERIENCE_LESS_THAN_FIVE_YEARS, _(u'Менее 5 лет')),
        (INSURANCE_EXPERIENCE_FROM_FIVE_TO_EIGHT_YEARS, _(u'От 5 до 8 лет')),
        (INSURANCE_EXPERIENCE_MORE_THAN_EIGHT_YEARS, _(u'8 лет и более')),
    )

    name = models.CharField(max_length=100)
    department = models.ForeignKey(to=Department)
    position = models.ForeignKey(to=Position)
    personnel_number = models.CharField(unique=True, max_length=100, verbose_name=_(u'табельный номер'))
    permanent_bonus_amount = models.DecimalField(max_digits=22, decimal_places=2)
    insurance_experience = models.SmallIntegerField(
        choices=INSURANCE_EXPERIENCE_CHOICES, default=INSURANCE_EXPERIENCE_LESS_THAN_FIVE_YEARS
    )
    hired = models.DateField()

    class Meta:
        verbose_name = _(u'сотрудник')
        verbose_name_plural = _(u'сотрудники')

    def get_sicktime(self, date):
        return self.sicktime_set.filter(
            start_date__lte=date,
            end_date__gte=date,
            active=True,
        ).first()

    def get_vacation(self, date):
        return self.vacation_set.filter(
            start_date__lte=date,
            end_date__gte=date,
            active=True,
        ).first()

    @property
    def wages(self):
        return self.permanent_bonus_amount + self.position.wages

    @property
    def last_two_years_wages(self):
        return self.wages * Decimal(24)

    @property
    def average_daily_earnings(self):
        return self.wages / Decimal(30)

    def get_bonus_payments(self, month):
        return self.bonus_set.filter(active=True, month=month).aggregate(
            Sum('amount')
        )['amount__sum'] or Decimal()



class Bonus(CommonModel):
    employee = models.ForeignKey(to=Employee)
    month = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(12),
            MinValueValidator(1)
        ]
    )
    year = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=22, decimal_places=2)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _(u'премия')
        verbose_name_plural = _(u'премии')

    @property
    def formatted_date(self, format_=u"{month:0>2}/{year}"):
        return format_.format(month=self.month, year=self.year)

    @property
    def percent(self):
        return (self.amount * Decimal(100)) / self.employee.wages

    def __unicode__(self):
        return u"{name} - {month_year} ({amount})".format(
            name=self.employee.name,
            month_year=self.formatted_date,
            amount=self.amount,
        )


class PaymentsQuerySet(models.QuerySet):
    def get_days_sum(self):
        return sum(map(lambda item: item.days_total, self))

    def get_payments_sum(self):
        return sum(map(lambda item: item.payments, self))


class SickTime(CommonModel):
    employee = models.ForeignKey(to=Employee)
    start_date = models.DateField()
    end_date = models.DateField()
    last_two_years_wages = models.DecimalField(max_digits=22, decimal_places=2)

    class Meta:
        verbose_name = _(u'больничный')
        verbose_name_plural = _(u'больничные')

    def __unicode__(self):
        return u"{name}: {start} - {end}".format(
            name=self.employee.name,
            start=self.start_date,
            end=self.end_date,
        )

    @property
    def day_rate(self):
        insurance_ratio = INSURANCE_RATIO[self.employee.insurance_experience]
        daily_wages = self.last_two_years_wages / ABSTRACT_RATIO
        if daily_wages < MINIMAL_DAILY_WAGES:
            daily_wages = MINIMAL_DAILY_WAGES
        if daily_wages > MAXIMUM_DAILY_WAGES:
            daily_wages = MAXIMUM_DAILY_WAGES
        return daily_wages * insurance_ratio


class Vacation(CommonModel):
    employee = models.ForeignKey(to=Employee)
    start_date = models.DateField()
    end_date = models.DateField()
    average_daily_earnings = models.DecimalField(max_digits=22, decimal_places=2)

    class Meta:
        verbose_name = _(u'отпуск')
        verbose_name_plural = _(u'отпуска')


    def __unicode__(self):
        return u"{name}: {start} - {end}".format(
            name=self.employee.name,
            start=self.start_date,
            end=self.end_date,
        )

    @property
    def day_rate(self):
        return self.average_daily_earnings
