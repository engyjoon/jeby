from urllib.parse import quote
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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
        keyword = quote(request.GET.get('keyword'))
        print(keyword)

    return render(
        request,
        'news/read.html',
    )
