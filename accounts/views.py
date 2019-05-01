import logging

from django.conf import settings
from django.contrib.auth import logout, login as auth_login, authenticate, REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView

from accounts.forms import UserCreationForm


logger = logging.getLogger('debugging')


def register(request):
    """User Register GET / POST"""
    logout(request)  # To make a session out

    if request.method == 'GET':
        reg_form = UserCreationForm()
        return render(request, 'accounts/register.html', {'reg_form': reg_form})

    """
    If the request method is POST, a form input will be requested.
    If the input is validated, will create a user and will be redirected to feed.
    else, return a view which is same with the GET which involved the error messages.   
    """
    with transaction.atomic():  # Queries will be committed if the below codes run without error.
        reg_form = UserCreationForm(data=request.POST)  # register
        if reg_form.is_valid():  # if get succeed to register then login the user.
            reg_form.save()

            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(request=request, username=username, password=password)
            auth_login(request, user)

            try:
                user.create_node()
            except Exception as e:
                logger.error('FAIL TO CREATE A USER NODE FOR {u}, {e}'.format(u=username, e=e))
            return redirect(settings.LOGIN_REDIRECT_URL)

        # To get the first among multiple errors.
        error_message = list(reg_form.errors.as_data().values())[0][0].message
    # There are some validation errors in the form. the errors are saved in form.errors.
    context = {'reg_form': reg_form, 'error_message': error_message}
    return render(request, 'accounts/register.html', context)


class LoginView(SuccessURLAllowedHostsMixin, FormView):
    """
    (Customized Django Built-in) Display the login form and handle the login action.
    """
    form_class = AuthenticationForm
    authentication_form = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'accounts/login.html'
    redirect_authenticated_user = False
    extra_context = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        else:
            logout(request)  # To make a session out.
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_form_class(self):
        return self.authentication_form or self.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update({
            self.redirect_field_name: self.get_redirect_url(),
            'site': current_site,
            'site_name': current_site.name,
            **(self.extra_context or {})
        })
        return context
