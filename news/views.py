import pprint as pp
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
    result = None
    if request.method == 'POST':
        result = naverapi.get_news(request.POST.get('keyword'))
        pp.pprint(result)

    return render(
        request,
        'news/read.html',
        {
            'news': result,
        }
    )
