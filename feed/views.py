from django.shortcuts import render

# Create your views here.


def feed(request):
    ct = {'user': request.user}
    return render(request, 'feed/index.html', ct)
