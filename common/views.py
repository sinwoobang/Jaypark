from django.shortcuts import render


def handle_not_fonud(request, exception=None):
    """Handler for 404"""
    return render(request, '404.html', status=404)
