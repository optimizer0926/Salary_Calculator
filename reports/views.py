# coding: utf-8
from __future__ import absolute_import

from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _

from common.models import Establishment
from common.mixins import (
    LoginRequiredMixin,
    XlsxResponseMixin,
)
from reports.reports import (
    SummaryReport,
    SickReport,
    VacationReport,
    BonusReport,
)
from reports.forms import ReportForm


class ReportListView(LoginRequiredMixin, ListView):
    template_name = 'reports/report_list.html'
    queryset = (
        {'name': _(u'Выплаты'), 'url': reverse_lazy('report-summary')},
        {'name': _(u'Премии'), 'url': reverse_lazy('report-bonus')},
        {'name': _(u'Больничные'), 'url': reverse_lazy('report-sick')},
        {'name': _(u'Отпуска'), 'url': reverse_lazy('report-vacation')},
    )


class ReportView(XlsxResponseMixin, FormView):
    template_name = 'reports/report_form.html'
    form_class = ReportForm
    report_class = NotImplemented
    report_title = NotImplemented

    def get_report_class(self):
        return self.report_class

    def get_content(self, context):
        establishment = Establishment.objects.last()
        report = self.get_report_class()(
            establishment=establishment,
            context=context,
        )
        return report.get_file_content()

    def form_valid(self, form):
        return self.render_to_file_response(form.cleaned_data)


class SummaryReportView(ReportView):
    report_class = SummaryReport
    report_title = _(u'Выплаты')
    filename = 'summary.xlsx'


class SickReportView(ReportView):
    report_class = SickReport
    report_title = _(u'Больничные')
    filename = 'sick.xlsx'


class VacationReportView(ReportView):
    report_class = VacationReport
    report_title = _(u'Отпуска')
    filename = 'vacation.xlsx'


class BonusReportView(ReportView):
    report_class = BonusReport
    report_title = _(u'Премии')
    filename = 'bonus.xlsx'
