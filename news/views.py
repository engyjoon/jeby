import urllib.parse
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import naverapi


@login_required(login_url='common:login')
def index(request):
    """뉴스 검색 첫 페이지"""

    return render(
        request,
        'news/index.html',
    )


def news_search(request):
    """키워드로 뉴스를 검색한다."""
    if request.method == 'GET':
        result = naverapi.get_news(request.GET.get('keyword'))

        print(result)

    return render(
        request,
        'news/read.html',
    )
