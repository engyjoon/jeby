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

    form = {}

    news = None
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        news = naverapi.get_news(keyword)
        form['keyword'] = keyword

    return render(
        request,
        'news/read.html',
        {
            'news': news,
            'form': form,
        }
    )
