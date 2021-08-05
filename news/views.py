import pprint as pp
from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Keyword
from . import naverapi


@login_required(login_url='common:login')
def index(request):
    """뉴스 검색 첫 페이지"""

    return render(
        request,
        'news/index.html',
    )


@login_required(login_url='common:login')
def news_search(request):
    """키워드로 뉴스를 검색한다."""

    form = {}
    error_msg = None
    template_name = 'news/read.html'

    news = None
    if request.method == 'POST':
        keyword = request.POST.get('keyword').strip()
        if keyword is None or keyword == '':
            error_msg = "키워드를 입력해 주세요."
            template_name = 'news/index.html'
        else:
            news = naverapi.get_news(keyword)
            form['keyword'] = keyword

    return render(
        request,
        template_name,
        {
            'news': news,
            'form': form,
            'error_msg': error_msg,
        }
    )


class KeywordList(LoginRequiredMixin, ListView):
    login_url = 'common:login'
    model = Keyword


class KeywordCreate(LoginRequiredMixin, CreateView):
    login_url = 'common:login'
    model = Keyword
    fields = ['title', 'content', 'mailing', 'shared']
