from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from accounts.models import UserProfile
from accounts.forms import UserEditForm, FullNameEditForm


class OwnerRequiredMixin(UserPassesTestMixin):
    def get_object(self, queryset=None):
        if not hasattr(self, '_cached_object'):
            self._cached_object = super().get_object(queryset)

        return self._cached_object

    def test_func(self):
        obj = self.get_object()
        return obj.user_id == self.request.user.id


class UserProfileUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserEditForm
    template_name = 'accounts/profile_edit.html'

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)

        if 'name_form' not in context:
            context['name_form'] = FullNameEditForm(instance=self.object.user)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        self.name_form = FullNameEditForm(request.POST, instance=self.object.user)
        profile_valid = form.is_valid()
        name_valid = self.name_form.is_valid()

        if profile_valid and name_valid:
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        self.name_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['name_form'] = self.name_form

        return self.render_to_response(context)

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'pk': self.object.pk})

