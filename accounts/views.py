import logging

from django.conf import settings
from django.contrib.auth import logout, login, authenticate
from django.db import transaction
from django.shortcuts import render, redirect
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
            login(request, user)

            try:
                user.create_node()
            except Exception as e:
                logger.error('FAIL TO CREATE A USER NODE FOR {u}, {e}'.format(u=username, e=e))
            return redirect(settings.LOGIN_REDIRECT_URL)

    # There are some validation errors in the form. the errors are saved in form.errors.
    return render(request, 'accounts/register.html', {'reg_form': reg_form})
