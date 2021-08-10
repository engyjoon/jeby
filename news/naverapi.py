import json
import re
from datetime import time, timedelta, datetime, timezone
import urllib.request
import urllib.parse
from dateutil.parser import parse
from django.conf import settings
from django.core.mail import send_mail
from .models import Setting, Keyword


KST = timezone(timedelta(hours=9))

news_list = {
    'yna.kr': {
        'id': 'yna', 'description': '연합뉴스',
    },
    'news.mk.co.kr': {
        'id': 'mk', 'description': '매일경제',
    },
    'news.jtbc.joins.com': {
        'id': 'jtbc', 'description': 'JTBC',
    },
    'www.hankyung.com': {
        'id': 'hankyung', 'description': '한국경제',
    },
    'news.joins.com': {
        'id': 'joins', 'description': '중앙일보',
    },
}


def get_news_group_site(keyword, display=50, start=1, sort='date'):
    items = get_news(keyword, display, start, sort)

    pattern = re.compile(r'^https?://([\w.-]*).*')

    result = []
    for item in items:
        website = pattern.search(item.get('originallink'))

        if website is not None:
            uri = website.group(1)
            item['pubDate'] = parse(item['pubDate'])

        if uri in news_list.keys():
            item['sitename'] = news_list.get(uri).get('description')
        else:
            item['sitename'] = 'unknown'

        result.append(item)

    return result


def send_email_by_schedule(current_time):
    now = datetime.now()
    rows = Setting.objects.all()
    for row in rows:
        times = row.email_send_time.split(';')
        if current_time in times:
            index = times.index(current_time)

            if index == 0:
                start_time = now.replace(
                    hour=0, minute=0, second=0, tzinfo=KST)
            else:
                _time = times[index-1].split(':')
                start_time = now.replace(
                    hour=int(_time[0]), minute=int(_time[1]), second=0, tzinfo=KST)

            _time = current_time.split(':')
            end_time = now.replace(
                hour=int(_time[0]), minute=int(_time[1]), second=0, tzinfo=KST)
            end_time = end_time + timedelta(seconds=-1)

        keywords = Keyword.objects.filter(author=row.author.id)
        keywords = keywords.filter(mailing=True)

        news = []
        for keyword in keywords:
            news = get_news_all(keyword.content, start_time)

        _recipients = row.email_recipient.split(';')
        recipients = []
        for recipient in _recipients:
            recipients.append(recipient.split(',')[1])

        _time = current_time.split(':')
        _now = now.replace(hour=int(_time[0]), minute=int(
            _time[1]), second=0, tzinfo=KST)
        mail_title = f'[뉴스] {_now.year}/{_now.month}/{_now.day} {_now.hour}시 {_now.minute}분'

        mail_content = '<table>'

        for new in news:
            mail_content += f'<tr><td>{new.get("title")}</td></tr>'

        mail_content += '</table>'

        send_mail(
            mail_title,
            mail_content,
            'jebyhouse@gmail.com',
            recipients,
            fail_silently=False,
        )

    return None


def get_news_all(keyword, start_time=None):
    items = []
    start = 1
    display = 100
    flag = True
    while flag:
        _list = get_news(keyword, display, start, 'date')

        for i in _list:
            if start_time and start_time > parse(i['pubDate']):
                flag = False
                break

            i['pubDate'] = parse(i['pubDate'])
            items.append(i)

        if len(_list) == display:
            start += 100

    return items


def get_news(keyword, display, start, sort):
    """네이버 뉴스 API 호출 및 결과 반환"""

    values = {
        'query': keyword,
        'display': display,
        'start': start,
        'sort': sort,
    }

    params = urllib.parse.urlencode(values, quote_via=urllib.parse.quote)

    url = "https://openapi.naver.com/v1/search/news.json?" + params

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", settings.NAVER_API_ID)
    request.add_header("X-Naver-Client-Secret", settings.NAVER_API_SECRET)

    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        result = json.loads(response_body.decode('utf-8')).get('items')
    else:
        print(rescode)
        result = None

    return result
