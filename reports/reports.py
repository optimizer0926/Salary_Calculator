# coding: utf-8
import datetime
import calendar
from decimal import Decimal
from collections import defaultdict
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from django.utils import dateformat
from django.utils.translation import ugettext as _
from django.conf import settings
from xlsxwriter.workbook import Workbook
from babel.dates import format_date

from common.utils import business_days
from common.utils import daterange
from personnel.models import (
    Employee,
    SickTime,
    TWOPLACES,
)

INCOME_TAX = Decimal("0.13")

def get_aggregated_data(employee, year, month):
    _, days_in_month_count = calendar.monthrange(year, month)
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, days_in_month_count)
    business_days_list = list(business_days(month, year))

    if start_date < employee.hired:
        start_date = employee.hired

    worked_days_count = 0
    worked_days_payments = Decimal('0.00')
    worked_days_rate = employee.wages / days_in_month_count
    vacation_days_count = 0
    vacation_payments = Decimal('0.00')
    sicktime_days_count = 0
    sicktime_payments = Decimal('0.00')
    for day in daterange(start_date, end_date):
        sicktime = employee.get_sicktime(day)
        if sicktime:
            sicktime_days_count +=1
            sicktime_payments += sicktime.day_rate
            continue
        vacation = employee.get_vacation(day)
        if vacation:
            vacation_days_count += 1
            vacation_payments += vacation.day_rate
            continue
        if day in business_days_list:
            worked_days_count += 1
        worked_days_payments += worked_days_rate
    sicktime_tax = sicktime_payments * INCOME_TAX
    sicktime_payments_minus_tax = sicktime_payments - sicktime_tax
    vacation_tax = vacation_payments * INCOME_TAX
    vacation_payments_minus_tax = vacation_payments - vacation_tax
    bonus_payments = employee.get_bonus_payments(month)
    bonus_tax = bonus_payments * INCOME_TAX
    bonus_payments_minus_tax = bonus_payments - bonus_tax
    total_payments = worked_days_payments + vacation_payments + sicktime_payments + bonus_payments
    total_tax = total_payments * INCOME_TAX
    total_payments_minus_tax = total_payments - total_tax
    return {
        'business_days_count': len(business_days_list),
        'worked_days_count': worked_days_count,
        'worked_days_payments': worked_days_payments.quantize(TWOPLACES),
        'vacation_days_count': vacation_days_count,
        'vacation_payments': vacation_payments.quantize(TWOPLACES),
        'vacation_tax': vacation_tax.quantize(TWOPLACES),
        'vacation_payments_minus_tax': vacation_payments_minus_tax.quantize(TWOPLACES),
        'sicktime_days_count': sicktime_days_count,
        'sicktime_payments': sicktime_payments.quantize(TWOPLACES),
        'sicktime_tax': sicktime_tax.quantize(TWOPLACES),
        'sicktime_payments_minus_tax': sicktime_payments_minus_tax.quantize(TWOPLACES),
        'total_payments': total_payments.quantize(TWOPLACES),
        'total_tax': total_tax.quantize(TWOPLACES),
        'total_payments_minus_tax': total_payments_minus_tax.quantize(TWOPLACES),
        'bonus_payments': bonus_payments.quantize(TWOPLACES),
        'bonus_tax': bonus_tax.quantize(TWOPLACES),
        'bonus_payments_minus_tax': bonus_payments_minus_tax.quantize(TWOPLACES),
    }


class Report(object):
    name = NotImplemented
    header = ()

    def __init__(self, establishment, context):
        self.establishment = establishment
        self.context = context
        self.file_content = None
        self.current_column = 0
        self.month, self.year = context.get('month_year', (1900, 1))

    def get_name(self):
        return self.name

    def get_queryset(self):
        return Employee.objects.filter(
            active=True,
            department__in=self.context.get('departments', []),
        )

    def build_report(self):
        output = StringIO.StringIO()
        book = Workbook(output)
        sheet = book.add_worksheet(self.get_name())
        self.write_header(sheet)
        self.write_body(sheet)
        self.write_footer(sheet)
        book.close()
        return output

    def write_header(self, sheet):
        report_date = datetime.date(self.year, self.month, 1)
        sheet.write(0, 0, self.establishment.name)
        sheet.write(2, 0, self.get_name())
        sheet.write(4, 0, _(u"за {pretty_month_year}").format(
            pretty_month_year=format_date(report_date, 'LLLL YYYY', locale=settings.LANGUAGE_CODE)
        ))
        for index, title in enumerate(self.header):
            sheet.write(6, index, title)
        self.current_column = 7

    def write_body(self, sheet):
        pass

    def write_footer(self, sheet):
        sheet.write(self.current_column + 2, 0, _(u'Гл. бухгалтер'))

    def get_file_content(self):
        if self.file_content is None:
            output = self.build_report()
            output.seek(0)
            self.file_content = output.read()
        return self.file_content


class SummaryReport(Report):
    name = _(u'Расчетная ведомость')
    header = (
        _(u'Номер п/п'),
        _(u'Табельный номер'),
        _(u'Фамилия Имя Отчество'),
        _(u'Занимаемая должность'),
        _(u'Отработано дней, часов'),
        _(u'Оплата по окладу'),
        _(u'Больничные'),
        _(u'Отпуска'),
        _(u'Итого начислено'),
        _(u'Удержано и зачтено, руб. НДФЛ'),
        _(u'Итого удержано'),
        _(u'Выплачено через кассу/банк'),
    )

    def write_body(self, sheet):
        index = 0
        summary = defaultdict(Decimal)
        for index, employee in enumerate(self.get_queryset()):
            aggregated_data = get_aggregated_data(employee, self.year, self.month)

            sheet.write(self.current_column + index, 0, index + 1)
            sheet.write(self.current_column + index, 1, employee.personnel_number)
            sheet.write(self.current_column + index, 2, employee.name)
            sheet.write(self.current_column + index, 3, employee.position.name)
            sheet.write(self.current_column + index, 4, aggregated_data['worked_days_count'])
            sheet.write(self.current_column + index, 5, aggregated_data['worked_days_payments'])
            sheet.write(self.current_column + index, 6, aggregated_data['sicktime_payments'])
            sheet.write(self.current_column + index, 7, aggregated_data['vacation_payments'])
            sheet.write(self.current_column + index, 8, aggregated_data['total_payments'])
            sheet.write(self.current_column + index, 9, aggregated_data['total_tax'])
            sheet.write(self.current_column + index, 10, aggregated_data['total_tax'])
            sheet.write(self.current_column + index, 11, aggregated_data['total_payments_minus_tax'])

            summary['payment'] += aggregated_data['worked_days_payments']
            summary['sick'] += aggregated_data['sicktime_payments']
            summary['vacation'] += aggregated_data['vacation_payments']
            summary['tax'] += aggregated_data['total_tax']
            summary['actual'] += aggregated_data['total_payments_minus_tax']

        self.current_column += index
        sheet.write(self.current_column + 1, 0, _(u'Итого по ведомости'))
        sheet.write(self.current_column + 1, 5, summary['payment'])
        sheet.write(self.current_column + 1, 6, summary['sick'])
        sheet.write(self.current_column + 1, 7, summary['vacation'])
        sheet.write(self.current_column + 1, 8, summary['payment'])
        sheet.write(self.current_column + 1, 9, summary['tax'])
        sheet.write(self.current_column + 1, 10, summary['tax'])
        sheet.write(self.current_column + 1, 11, summary['actual'])


class SickReport(Report):
    name = _(u'Расчетная ведомость')
    header = (
        _(u'Номер п/п'),
        _(u'Табельный номер'),
        _(u'Фамилия Имя Отчество'),
        _(u'Занимаемая должность'),
        _(u'Больничный'),
        _(u'Итого начислено'),
        _(u'Удержано и зачтено, руб. НДФЛ'),
        _(u'Итого удержано'),
        _(u'Выплачено через кассу/банк'),
    )

    def write_body(self, sheet):
        summary = defaultdict(Decimal)
        for index, employee in enumerate(self.get_queryset()):
            aggregated_data = get_aggregated_data(employee, self.year, self.month)

            sheet.write(self.current_column + index, 0, index + 1)
            sheet.write(self.current_column + index, 1, employee.personnel_number)
            sheet.write(self.current_column + index, 2, employee.name)
            sheet.write(self.current_column + index, 3, employee.position.name)
            sheet.write(self.current_column + index, 4, aggregated_data['sicktime_payments'])
            sheet.write(self.current_column + index, 5, aggregated_data['sicktime_payments'])
            sheet.write(self.current_column + index, 6, aggregated_data['sicktime_tax'])
            sheet.write(self.current_column + index, 7, aggregated_data['sicktime_tax'])
            sheet.write(self.current_column + index, 8, aggregated_data['sicktime_payments_minus_tax'])

            summary['sicktime'] += aggregated_data['sicktime_payments']
            summary['tax'] += aggregated_data['sicktime_tax']
            summary['actual'] += aggregated_data['sicktime_payments_minus_tax']

        self.current_column += index
        sheet.write(self.current_column + 1, 0, _(u'Итого по ведомости'))
        sheet.write(self.current_column + 1, 4, summary['sicktime'])
        sheet.write(self.current_column + 1, 5, summary['sicktime'])
        sheet.write(self.current_column + 1, 6, summary['tax'])
        sheet.write(self.current_column + 1, 7, summary['tax'])
        sheet.write(self.current_column + 1, 8, summary['actual'])


class VacationReport(Report):
    name = _(u'Расчетная ведомость')
    header = (
        _(u'Номер п/п'),
        _(u'Табельный номер'),
        _(u'Фамилия Имя Отчество'),
        _(u'Занимаемая должность'),
        _(u'Отпускные'),
        _(u'Итого начислено'),
        _(u'Удержано и зачтено, руб. НДФЛ'),
        _(u'Итого удержано'),
        _(u'Выплачено через кассу/банк'),
    )

    def write_body(self, sheet):
        summary = defaultdict(Decimal)
        for index, employee in enumerate(self.get_queryset()):
            aggregated_data = get_aggregated_data(employee, self.year, self.month)

            sheet.write(self.current_column + index, 0, index + 1)
            sheet.write(self.current_column + index, 1, employee.personnel_number)
            sheet.write(self.current_column + index, 2, employee.name)
            sheet.write(self.current_column + index, 3, employee.position.name)
            sheet.write(self.current_column + index, 4, aggregated_data['vacation_payments'])
            sheet.write(self.current_column + index, 5, aggregated_data['vacation_payments'])
            sheet.write(self.current_column + index, 6, aggregated_data['vacation_tax'])
            sheet.write(self.current_column + index, 7, aggregated_data['vacation_tax'])
            sheet.write(self.current_column + index, 8, aggregated_data['vacation_payments_minus_tax'])

            summary['vacation'] += aggregated_data['vacation_payments']
            summary['tax'] += aggregated_data['vacation_tax']
            summary['actual'] += aggregated_data['vacation_payments_minus_tax']

        self.current_column += index
        sheet.write(self.current_column + 1, 0, _(u'Итого по ведомости'))
        sheet.write(self.current_column + 1, 4, summary['vacation'])
        sheet.write(self.current_column + 1, 5, summary['vacation'])
        sheet.write(self.current_column + 1, 6, summary['tax'])
        sheet.write(self.current_column + 1, 7, summary['tax'])
        sheet.write(self.current_column + 1, 8, summary['actual'])


class BonusReport(Report):
    name = _(u'Расчетная ведомость')
    header = (
        _(u'Номер п/п'),
        _(u'Табельный номер'),
        _(u'Фамилия Имя Отчество'),
        _(u'Занимаемая должность'),
        _(u'Премия'),
        _(u'Итого начислено'),
        _(u'Удержано и зачтено, руб. НДФЛ'),
        _(u'Итого удержано'),
        _(u'Выплачено через кассу/банк'),
    )

    def write_body(self, sheet):
        summary = defaultdict(Decimal)
        for index, employee in enumerate(self.get_queryset()):
            aggregated_data = get_aggregated_data(employee, self.year, self.month)

            sheet.write(self.current_column + index, 0, index + 1)
            sheet.write(self.current_column + index, 1, employee.personnel_number)
            sheet.write(self.current_column + index, 2, employee.name)
            sheet.write(self.current_column + index, 3, employee.position.name)
            sheet.write(self.current_column + index, 4, aggregated_data['bonus_payments'])
            sheet.write(self.current_column + index, 5, aggregated_data['bonus_payments'])
            sheet.write(self.current_column + index, 6, aggregated_data['bonus_tax'])
            sheet.write(self.current_column + index, 7, aggregated_data['bonus_tax'])
            sheet.write(self.current_column + index, 8, aggregated_data['bonus_payments_minus_tax'])

            summary['bonus'] += aggregated_data['bonus_payments']
            summary['tax'] += aggregated_data['bonus_tax']
            summary['actual'] += aggregated_data['bonus_payments_minus_tax']

        self.current_column += index
        sheet.write(self.current_column + 1, 0, _(u'Итого по ведомости'))
        sheet.write(self.current_column + 1, 4, summary['bonus'])
        sheet.write(self.current_column + 1, 5, summary['bonus'])
        sheet.write(self.current_column + 1, 6, summary['tax'])
        sheet.write(self.current_column + 1, 7, summary['tax'])
        sheet.write(self.current_column + 1, 8, summary['actual'])
