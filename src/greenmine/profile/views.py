# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.timezone import now
from django.views.decorators.csrf import ensure_csrf_cookie

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required, staff_required

# Temporal imports
from greenmine.base.models import *
from greenmine.scrum.models import *

from greenmine.core.utils import iter_points
from greenmine.core import signals

from .forms import *
from .models import Profile

import os
import re
from datetime import timedelta



class RegisterView(GenericView):
    template_path = 'register.html'

    def get(self, request):
        if settings.DISABLE_REGISTRATION:
            messages.warning(request, _(u"Registration system is disabled."))

        form = RegisterForm()
        context = {'form':form}
        return self.render_to_response(self.template_path, context)

    def post(self, request):
        if settings.DISABLE_REGISTRATION:
            return self.render_redirect(reverse('register'))

        form = RegisterForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return self.render_to_response(self.template_path, context)

        user = User(
            username = form.cleaned_data['username'],
            first_name = form.cleaned_data['first_name'],
            last_name = form.cleaned_data['last_name'],
            email = form.cleaned_data['email'],
            is_active = False,
            is_staff = False,
            is_superuser = False,
        )
        user.set_password(form.cleaned_data['password'])
        user.save()

        signals.mail_new_user.send(sender=self, user=user)
        #messages.info(request, _(u"Validation message was sent successfully."))
        return self.render_redirect(reverse('login'))



class AccountActivation(GenericView):
    def get(self, request, token):
        try:
            profile = Profile.objects.get(token=token)
            profile.user.is_active = True
            profile.token = None

            profile.user.save()
            profile.save()

            messages.info(request, _(u"User %(username)s is now activated!") % \
                {'username': profile.user.username})

        except Profile.DoesNotExist:
            messages.error(request, _(u"Invalid token"))

        return self.render_redirect(reverse("login"))



class RememberPasswordView(GenericView):
    """
    Remember password procedure for non logged users.
    This sends the password revery mail with link for
    a recovery procedure.
    """

    template_name = 'remember-password.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        form = ForgottenPasswordForm()

        return self.render_to_response(self.template_name,
            {'form': form})

    def post(self, request):
        form = ForgottenPasswordForm(request.POST)
        if form.is_valid():
            form.user.set_unusable_password()
            form.user.save()

            signals.mail_recovery_password.send(sender=self, user=form.user)
            messages.info(request, _(u'He has sent an email with the link to retrieve your password'))

            return self.render_to_ok({'redirect_to':'/'})

        response = {'errors': form.errors}
        return self.render_to_error(response)



class PasswordChangeView(GenericView):
    """
    User profile - password change view.
    """

    template_path = 'password.html'

    @login_required
    def get(self, request):
        form = PasswordRecoveryForm()
        context = {'form': form}
        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request):
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            messages.info(request, _(u"Password changed!"))
            return self.render_redirect(reverse('profile'))

        context = {'form': form}
        return self.render_to_response(self.template_path, context)


class PasswordRecoveryView(GenericView):
    """
    Simple recovery password procedure.
    """

    template_name = "password_recovery.html"

    def get(self, request, token):
        form = PasswordRecoveryForm()
        context = {'form':form}
        return self.render_to_response(self.template_name, context)

    def post(self, request, token):
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            profile_queryset = Profile.objects.filter(token=token)
            if not profile_queryset:
                messages.error(request, _(u'Token has expired, try again'))
                return self.render_redirect(reverse('login'))

            profile = profile_queryset.get()
            user = profile.user
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile.token = None
            profile.save()

            messages.info(request, _(u'The password has been successfully restored.'))
            return self.render_redirect(reverse('login'))

        context = {'form':form}
        return self.render_to_response(self.template_name, context)


class ProfileView(GenericView):
    template_name = 'profile.html'

    @login_required
    def get(self, request):
        form = ProfileForm(instance=request.user)
        context = {'form':form}
        return self.render_to_response(self.template_name, context)

    @login_required
    @transaction.commit_on_success
    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        context = {'form':form}

        if not form.is_valid():
            return self.render_json.error(form.errors)

        sem = transaction.savepoint()
        try:
            request.user = form.save()
        except IntegrityError as e:
            transaction.savepoint_rollback(sem)

            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render_to_response(self.template_name, context)

        transaction.savepoint_commit(sem)
        #messages.info(request, _(u'Profile save success!'))
        #return HttpResponseRedirect(reverse('profile'))
        return self.render_json({'redirect_to': reverse('profile')})


class LoginView(GenericView):
    template_name = 'login.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        login_form = LoginForm(request=request)

        context = {
            'form': login_form,
            'register_disabled': settings.DISABLE_REGISTRATION,
        }

        return self.render_to_response(self.template_name, context)

    def post(self, request):
        login_form = LoginForm(request.POST, request=request)
        if request.is_ajax():
            if login_form.is_valid():
                user_profile = login_form._user.get_profile()
                if user_profile.default_language:
                    request.session['django_language'] = user_profile.default_language

                return self.render_to_ok({'redirect_to':'/'})

            return self.render_json_error(login_form.errors)
        return self.render_json({'error_msg':'Invalid request'}, ok=False)


