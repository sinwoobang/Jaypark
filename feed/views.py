from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def feed(request):
    ct = {'user': request.user}
    return render(request, 'feed/index.html', ct)
