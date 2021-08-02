from django.shortcuts import render


def login(request):
    return render(
        request,
        'single_pages/login.html',
    )
