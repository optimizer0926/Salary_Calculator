# coding:utf-8
from datetime import datetime
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from xlsxwriter.workbook import Workbook


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class XlsxResponseMixin(object):
    mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    filename = NotImplemented

    def get_filename(self):
        return self.filename

    def get_content(self, context):
        raise NotImplementedError('``get_content()`` method is not implemented')

    def render_to_file_response(self, context, **response_kwargs):
        output = self.get_content(context)
        response = HttpResponse(output, content_type=self.mimetype)

        response['Content-Disposition'] = "attachment; filename={filename}".format(
            filename=self.get_filename(),
        )

        return response


class CleanMonthYearMixin(object):
    def clean_month_year(self):
        try:
            value = datetime.strptime(
                self.cleaned_data['month_year'],
                self.fields['month_year'].widget.format
            )
        except ValueError:
            raise ValidationError(
                _(u'Неверный формат: данные должны соответствовать формату "ММ/ГГГГ"'),
            )
        return (value.month, value.year)


class ActiveObjectsMixin(object):
    def get_queryset(self):
        return super(ActiveObjectsMixin, self).get_queryset().filter(active=True)
