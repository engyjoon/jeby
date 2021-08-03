from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='common:login')
def index(request):
    return render(
        request,
        'news/index.html',
    )
