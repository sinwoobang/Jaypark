from django.http import HttpResponse
from django.shortcuts import render


def handle_not_fonud(request, exception=None):
    """Handler for 404"""
    return render(request, '404.html', status=404)


def health(request):
    """Health Check API"""
    return HttpResponse('ok')
