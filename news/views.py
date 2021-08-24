import pprint as pp

from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.core.exceptions import PermissionDenied

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .models import Keyword, Setting, Site
from .serializers import SiteSerializer
from . import naverapi


@login_required(login_url='common:login')
def index(request):
    """
    뉴스 검색 첫 페이지
    """

    keywords = Keyword.objects.all()

    return render(
        request,
        'news/index.html',
        {
            'keywords': keywords,
        }
    )


@login_required(login_url='common:login')
def news_search(request):
    """
    키워드로 뉴스를 검색한다.
    """

    form = {}
    error_msg = None
    template_name = 'news/read.html'

    # 사용자가 등록한 키워드를 조회하여 반환한다.
    current_user = request.user
    keywords = Keyword.objects.filter(author=current_user)

    news = None
    if request.method == 'POST':
        keyword = request.POST.get('keyword').strip()

        # 키워드를 입력하지 않을 경우 관련 메지지를 반환한다.
        if keyword is None or keyword == '':
            error_msg = "키워드를 입력해 주세요."
        # 키워드를 입력했을 경우 최근 24간 뉴스 리스트를 반환한다.
        else:
            news = naverapi.get_news_by_hour(keyword, start_hour=24)
            form['keyword'] = keyword

    return render(
        request,
        template_name,
        {
            'news': news,
            'form': form,
            'error_msg': error_msg,
            'keywords': keywords,
        }
    )


class KeywordList(LoginRequiredMixin, ListView):
    """
    """

    login_url = 'common:login'
    model = Keyword

    def get_queryset(self):
        current_user = self.request.user
        keyword_list = Keyword.objects.filter(author=current_user)

        return keyword_list


class KeywordCreate(LoginRequiredMixin, CreateView):
    """
    """

    login_url = 'common:login'
    success_url = reverse_lazy('news:keyword')
    model = Keyword
    fields = ['title', 'content', 'mailing', 'shared']

    def form_valid(self, form):
        keyword_last = Keyword.objects.last()
        if keyword_last:
            form.instance.order = keyword_last.pk + 1
        else:
            form.instance.order = 1

        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            response = super(KeywordCreate, self).form_valid(form)

            return response
        else:
            return redirect('news:keyword')


class KeywordUpdate(LoginRequiredMixin, UpdateView):
    """
    """

    login_url = 'common:login'
    success_url = reverse_lazy('news:keyword')
    model = Keyword
    fields = ['title', 'content', 'mailing', 'shared']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(KeywordUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


@login_required(login_url='common:login')
def keyword_delete(request, pk):
    """
    """

    keyword = get_object_or_404(Keyword, pk=pk)
    if request.user == keyword.author:
        keyword.delete()
        return redirect('news:keyword')
    else:
        raise PermissionDenied


@login_required(login_url='common:login')
def email_setting(request):
    """
    """

    # setting = get_object_or_404(Setting, author=request.user.id)
    settings = Setting.objects.filter(author=request.user.id)

    email_send_times = None
    email_recipients = None

    if settings.exists():
        for setting in settings:
            email_send_times = setting.email_send_time
            email_recipients = setting.email_recipient

    return render(
        request,
        'news/email_setting.html',
        {
            'email_send_times': email_send_times,
            'email_recipients': email_recipients,
        }
    )


class SiteCreateGenericAPIView(generics.CreateAPIView):
    serializer_class = SiteSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


class SiteUpdateGenericAPIView(generics.UpdateAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
