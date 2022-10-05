from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.core.exceptions import PermissionDenied

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .models import Keyword, Recipient, Setting, Site
from .serializers import SiteSerializer
from . import naverapi, utils


@login_required(login_url="common:login")
def index(request):
    """
    뉴스 검색 첫 페이지를 반환한다.
    """
    keywords = Keyword.objects.all()

    return render(
        request,
        "news/index.html",
        {
            "keywords": keywords,
        },
    )


@login_required(login_url="common:login")
def news_search(request):
    """
    키워드 검색 페이지에서 사용한다.
    키워드로 뉴스를 검색한다.
    """
    form = {}
    error_msg = None
    template_name = "news/read.html"

    # 사용자가 등록한 키워드를 조회하여 반환한다.
    current_user = request.user
    keywords = Keyword.objects.filter(author=current_user)

    # 수신자를 조회한다.
    email_users = Recipient.objects.filter(author=current_user)

    news = None

    if request.method == "GET":
        return render(
            request,
            template_name,
            {
                "keywords": keywords,
                "email_users": email_users,
            },
        )
    elif request.method == "POST":
        keyword = request.POST.get("keyword").strip()

        # 키워드를 입력하지 않을 경우 관련 메지지를 반환한다.
        if keyword is None or keyword == "":
            error_msg = "키워드를 입력해 주세요."
        # 키워드를 입력했을 경우 최근 24간 뉴스 리스트를 반환한다.
        else:
            if current_user.username == "imsi":
                news = naverapi.get_news_from_january(keyword)
            else:
                news = naverapi.get_news_by_hour(keyword, start_hour=24)
            form["keyword"] = keyword

        return render(
            request,
            template_name,
            {
                "news": news,
                "form": form,
                "error_msg": error_msg,
                "keywords": keywords,
                "email_users": email_users,
            },
        )


class KeywordList(LoginRequiredMixin, ListView):
    """
    키워드 관리 페이지에서 사용한다.
    키워드 리스트를 반환한다.
    """

    login_url = "common:login"
    model = Keyword

    def get_queryset(self):
        current_user = self.request.user
        keyword_list = Keyword.objects.filter(author=current_user)

        return keyword_list


class KeywordCreate(LoginRequiredMixin, CreateView):
    """
    키워드 관리 페이지에서 사용한다.
    키워드를 생성한다.
    """

    login_url = "common:login"
    success_url = reverse_lazy("news:keyword")
    model = Keyword
    fields = ["title", "content", "mailing", "shared"]

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
            return redirect("news:keyword")


class KeywordUpdate(LoginRequiredMixin, UpdateView):
    """
    키워드 관리 페이지에서 사용한다.
    키워드를 수정한다.
    """

    login_url = "common:login"
    success_url = reverse_lazy("news:keyword")
    model = Keyword
    fields = ["title", "content", "mailing", "shared"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(KeywordUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


@login_required(login_url="common:login")
def keyword_delete(request, pk):
    """
    키워드 관리 페이지에서 사용한다.
    키워드를 삭제한다.
    """
    keyword = get_object_or_404(Keyword, pk=pk)
    if request.user == keyword.author:
        keyword.delete()
        return redirect("news:keyword")
    else:
        raise PermissionDenied


class RecipientList(LoginRequiredMixin, ListView):
    """
    수신자 관리 페이지에서 사용한다.
    수신자 리스트를 반환한다.
    """

    login_url = "common:login"
    model = Recipient

    def get_queryset(self):
        current_user = self.request.user
        recipient_list = Recipient.objects.filter(author=current_user)

        return recipient_list


class RecipientCreate(LoginRequiredMixin, CreateView):
    """
    수신자 관리 페이지에서 사용한다.
    수신자를 생성한다.
    """

    login_url = "common:login"
    success_url = reverse_lazy("news:recipient")
    model = Recipient
    fields = ["name", "email", "note"]

    def form_valid(self, form):
        recipient_last = Recipient.objects.last()
        if recipient_last:
            form.instance.order = recipient_last.order + 1
        else:
            form.instance.order = 1

        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            response = super(RecipientCreate, self).form_valid(form)

            return response
        else:
            return redirect("news:recipient")


class RecipientUpdate(LoginRequiredMixin, UpdateView):
    """
    수신자 관리 페이지에서 사용한다.
    수신자를 수정한다.
    """

    login_url = "common:login"
    success_url = reverse_lazy("news:recipient")
    model = Recipient
    fields = ["name", "email", "note"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(RecipientUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


@login_required(login_url="common:login")
def recipient_delete(request, pk):
    """
    수신자 관리 페이지에서 사용한다.
    수신자를 삭제한다.
    """
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.user == recipient.author:
        recipient.delete()
        return redirect("news:recipient")
    else:
        raise PermissionDenied


class SiteCreateGenericAPIView(generics.CreateAPIView):
    """
    뉴스 검색 페이지에서 언론사를 생성하면 호출된다.
    """

    serializer_class = SiteSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


class SiteUpdateGenericAPIView(generics.UpdateAPIView):
    """
    뉴스 검색 페이지에서 언론사를 수정하면 호출된다.
    """

    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


@login_required(login_url="common:login")
@api_view(["GET", "POST"])
def share_news(request):
    """
    뉴스 검색 후 선택한 뉴스를 공유하면
    지정된 수신자에게 선택한 뉴스를 이메일로 발송한다.
    """
    if request.method == "POST":
        data = request.data
        utils.send_email_by_share(data)

        return JsonResponse({"result": "success"})


@login_required(login_url="common:login")
def email_setting(request):
    """
    이메일설정 페이지에서 사용한다.
    이메일 설정 정보를 반환한다.
    """
    current_user = request.user

    # setting model과 선택한 이메일 수신자를 조회한다.
    try:
        setting = Setting.objects.get(author=request.user.id)
    except Setting.DoesNotExist:
        setting = Setting()
        setting.author = current_user
        setting.save()

    # 선택한 이메일 수신자를 조회한다.
    setting_recipients = setting.email_recipients.all()

    # 선택 가능한 이메일 수신자를 조회한다.
    try:
        recipients = Recipient.objects.filter(author=current_user)
    except Recipient.DoesNotExist:
        recipients = None

    return render(
        request,
        "news/email_setting.html",
        {
            "setting": setting,
            "setting_recipients": setting_recipients,
            "recipients": recipients,
        },
    )


class SettingUpdate(LoginRequiredMixin, UpdateView):
    """
    이메일 설정 페이지에서 사용한다.
    발송시간, 업무시간, 수신자를 수정한다.
    """

    login_url = "common:login"
    success_url = reverse_lazy("news:email_setting")
    model = Setting
    template_name = "news/email_setting.html"
    fields = ["email_send_time", "work_hour", "email_recipients"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(SettingUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(SettingUpdate, self).form_valid(form)
        self.object.email_recipients.clear()

        email_recipients_str = self.request.POST.get("email_recipients_str")
        if email_recipients_str:
            _list = email_recipients_str.split(";")
            for pk in _list:
                recipient = Recipient.objects.get(pk=pk)
                self.object.email_recipients.add(recipient)

        return response
