import json
import re
import urllib.request
import urllib.parse
from django.conf import settings


news_list = {
    'news.naver.com': 'naver',
}


def get_news(keyword):
    """네이버 뉴스 API 호출 및 결과 반환"""

    values = {
        'query': urllib.parse.quote(keyword),
        'display': 5,
        'start': 1,
        'sort': 'date',
    }

    params = urllib.parse.urlencode(values)

    url = "https://openapi.naver.com/v1/search/news.json?" + params

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", settings.NAVER_API_ID)
    request.add_header("X-Naver-Client-Secret", settings.NAVER_API_SECRET)

    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        items = json.loads(response_body.decode('utf-8')).get('items')

        pattern = re.compile(r'^https?://([\w.-]*).*')

        news_by_website = {}
        for item in items:
            website = pattern.search(item.get('link'))
            link = website.group(1)

            if link in news_list.keys():
                link = news_list.get(link)
            else:
                link = 'etc'

            news_by_website.setdefault(link, [])
            news_by_website.get(link).append(item)

        result = news_by_website
    else:
        result = None

    return result
