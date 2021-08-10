import json
import re
from datetime import time, timedelta
import urllib.request
import urllib.parse
from django.conf import settings
from .models import Setting, Keyword


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
            item['pubDate'] = item['pubDate'].split()[4]

        if uri in news_list.keys():
            item['sitename'] = news_list.get(uri).get('description')
        else:
            item['sitename'] = 'unknown'

        result.append(item)

    return result


def get_news_by_schedule(current_time):
    rows = Setting.objects.all()
    for row in rows:
        times = row.email_send_time.split(';')
        if current_time in times:
            index = times.index(current_time)

            if index == 0:
                start_time = time(0, 0, 0)
            else:
                _time = times[index-1].split(':')
                start_time = time(int(_time[0]), int(_time[1]), 0)

            _time = current_time.split(':')
            end_time = time(int(_time[0]), int(_time[1]), 0)

            if end_time.minute == 0:
                end_time = time(end_time.hour-1, 59, 59)
            else:
                end_time = time(
                    end_time.hour, end_time.minute-1, end_time.second)

        keywords = Keyword.objects.filter(author=row.author.id)
        keywords = keywords.filter(mailing=True)

        for keyword in keywords:
            print(keyword.content)

        # recipients = row.email_recipient.split(';')

    return None


def get_news_all(keyword):

    return None


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
