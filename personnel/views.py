# coding:utf-8
import simplejson as json
from django.views.generic.list import ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from personnel.models import (
    Department,
    Position,
    Employee,
    Bonus,
    SickTime,
    Vacation,
    TWOPLACES,
)
from common.views import (
    AutoPopulatedCreateView,
    AutoPopulatedUpdateView,
    SalarycalcDeleteView,
)
from common.mixins import (
    LoginRequiredMixin,
    ActiveObjectsMixin,
)
from personnel.forms import (
    DepartmentForm,
    EmployeeForm,
    PositionForm,
    BonusCreateForm,
    BonusUpdateForm,
    SickTimeCreateForm,
    SickTimeUpdateForm,
    VacationCreateForm,
    VacationUpdateForm,
)


class DepartmentListView(LoginRequiredMixin, ActiveObjectsMixin, ListView):
    model = Department


class DepartmentCreateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedCreateView):
    model = Department
    form_class = DepartmentForm
    success_url = reverse_lazy('department-list')
    success_message = _(u'Отдел "%(name)s" создан')


class DepartmentUpdateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedUpdateView):
    model = Department
    form_class = DepartmentForm
    success_url = reverse_lazy('department-list')
    success_message = _(u'Отдел "%(name)s" обновлён')


class DepartmentDeleteView(LoginRequiredMixin, SalarycalcDeleteView):
    model = Department
    success_url = reverse_lazy('department-list')
    success_message = _(u'Отдел удалён')

    def delete_success(self):
        self.object.employee_set.update(active=False)
        super(DepartmentDeleteView, self).delete_success()


class PositionListView(LoginRequiredMixin, ActiveObjectsMixin, ListView):
    model = Position


class PositionCreateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedCreateView):
    model = Position
    form_class = PositionForm
    success_url = reverse_lazy('position-list')
    success_message = _(u'Должность "%(name)s" создана')


class PositionUpdateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedUpdateView):
    model = Position
    form_class = PositionForm
    success_url = reverse_lazy('position-list')
    success_message = _(u'Должность "%(name)s" обновлена')


class PositionDeleteView(LoginRequiredMixin, SalarycalcDeleteView):
    model = Position
    success_url = reverse_lazy('position-list')
    success_message = _(u'Должность удалена')


class EmployeeListView(LoginRequiredMixin, ActiveObjectsMixin, ListView):
    model = Employee

    def get_queryset(self):
        queryset = super(EmployeeListView, self).get_queryset()
        return queryset.filter(
            department_id=self.kwargs.get('department_id'),
        )

    def get_context_data(self, **kwargs):
        data = super(EmployeeListView, self).get_context_data(**kwargs)
        department = get_object_or_404(Department, pk=self.kwargs['department_id'])
        data['department'] = department
        return data


class EmployeeCreateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedCreateView):
    model = Employee
    form_class = EmployeeForm
    success_url = reverse_lazy('department-list')
    success_message = _(u'Сотрудник "%(name)s" создан')

    def get_form_kwargs(self):
        kwargs = super(EmployeeCreateView, self).get_form_kwargs()
        department = get_object_or_404(Department, pk=self.kwargs['department_id'])
        kwargs['initial']['department'] = department
        return kwargs


class EmployeeUpdateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedUpdateView):
    model = Employee
    form_class = EmployeeForm
    success_url = reverse_lazy('department-list')
    success_message = _(u'Сотрудник "%(name)s" обновлён')

    def get_form_kwargs(self):
        kwargs = super(EmployeeUpdateView, self).get_form_kwargs()
        kwargs['initial']['department'] = self.object.department
        return kwargs


class EmployeeDeleteView(LoginRequiredMixin, SalarycalcDeleteView):
    model = Employee
    success_url = reverse_lazy('department-list')
    success_message = _(u'Сотрудник удалён')


class BonusListView(LoginRequiredMixin, ActiveObjectsMixin, ListView):
    model = Bonus


class BonusCreateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedCreateView):
    model = Bonus
    form_class = BonusCreateForm
    success_url = reverse_lazy('bonus-list')
    success_message = _(u'Премия создана')


class BonusUpdateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedUpdateView):
    model = Bonus
    form_class = BonusUpdateForm
    success_url = reverse_lazy('bonus-list')
    success_message = _(u'Премия обновлена')

    def get_initial(self):
        initial = super(BonusUpdateView, self).get_initial()
        initial['percent'] = self.object.percent
        return initial


class BonusDeleteView(LoginRequiredMixin, SalarycalcDeleteView):
    model = Bonus
    success_url = reverse_lazy('bonus-list')
    success_message = _(u'Премия удалена')


class SickTimeListView(LoginRequiredMixin, ActiveObjectsMixin,  ListView):
    model = SickTime


class SickTimeCreateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedCreateView):
    model = SickTime
    form_class = SickTimeCreateForm
    template_name = 'personnel/sicktime_create_form.html'
    success_url = reverse_lazy('sicktime-list')
    success_message = _(u'Больничный создан')

    def get_context_data(self, *args, **kwargs):
        context = super(SickTimeCreateView, self).get_context_data(*args, **kwargs)
        context['employees_last_two_years_wages'] = json.dumps({
            employee.pk: str(employee.last_two_years_wages.quantize(TWOPLACES))
            for employee in Employee.objects.filter(active=True)
        })
        return context


class SickTimeUpdateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedUpdateView):
    model = SickTime
    form_class = SickTimeUpdateForm
    success_url = reverse_lazy('sicktime-list')
    success_message = _(u'Больничный обновлён')


class SickTimeDeleteView(LoginRequiredMixin, SalarycalcDeleteView):
    model = SickTime
    success_url = reverse_lazy('sicktime-list')
    success_message = _(u'Больничный удалён')


class VacationListView(LoginRequiredMixin, ActiveObjectsMixin, ListView):
    model = Vacation


class VacationCreateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedCreateView):
    model = Vacation
    form_class = VacationCreateForm
    template_name = 'personnel/vacation_create_form.html'
    success_url = reverse_lazy('vacation-list')
    success_message = _(u'Отпуск создан')

    def get_context_data(self, *args, **kwargs):
        context = super(VacationCreateView, self).get_context_data(*args, **kwargs)
        context['employees_average_daily_earnings'] = json.dumps({
            employee.pk: str(employee.average_daily_earnings.quantize(TWOPLACES))
            for employee in Employee.objects.filter(active=True)
        })
        return context


class VacationUpdateView(SuccessMessageMixin, LoginRequiredMixin, AutoPopulatedUpdateView):
    model = Vacation
    form_class = VacationUpdateForm
    success_url = reverse_lazy('vacation-list')
    success_message = _(u'Отпуск обновлён')


class VacationDeleteView(LoginRequiredMixin, SalarycalcDeleteView):
    model = Vacation
    success_url = reverse_lazy('vacation-list')
    success_message = _(u'Отпуск удалён')
