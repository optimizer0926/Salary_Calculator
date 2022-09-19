# coding:utf-8
from datetime import datetime

from django.http import HttpResponseRedirect
from django.views.generic.edit import (
    DeleteView,
    CreateView,
    UpdateView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


class SalarycalcDeleteView(DeleteView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.active=False
        self.object.save()
        self.delete_success()
        return HttpResponseRedirect(success_url)

    def delete_success(self):
        messages.success(self.request, self.success_message)


class AutoPopulatedCreateView(CreateView):
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.created_date = datetime.now()
        form.instance.updated_date = datetime.now()
        return super(AutoPopulatedCreateView, self).form_valid(form)


class AutoPopulatedUpdateView(UpdateView):
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.updated_date = datetime.now()
        return super(AutoPopulatedUpdateView, self).form_valid(form)
