import json
import re
import urllib.request
import urllib.parse
from django.conf import settings


news_list = {
    'yna.kr': {
        'id': 'yna',
        'description': '연합뉴스',
    },
    'news.mk.co.kr': {
        'id': 'mk',
        'description': '매일경제',
    },
    'news.jtbc.joins.com': {
        'id': 'jtbc',
        'description': 'JTBC',
    },
    'www.hankyung.com': {
        'id': 'hankyung',
        'description': '한국경제',
    },
    'news.joins.com': {
        'id': 'joins',
        'description': '중앙일보',
    },
}


def get_news(keyword):
    """네이버 뉴스 API 호출 및 결과 반환"""

    values = {
        'query': keyword,
        'display': 50,
        'start': 1,
        'sort': 'date',
    }

    params = urllib.parse.urlencode(values, quote_via=urllib.parse.quote)
    print(params)

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
            website = pattern.search(item.get('originallink'))

            if website is not None:
                link = website.group(1)

                item['pubDate'] = item['pubDate'].split()[4]

                if link in news_list.keys():
                    # siteid = news_list.get(link).get('id')
                    siteid = 'major'
                    item['sitename'] = news_list.get(link).get('description')
                else:
                    siteid = 'etc'
                    item['sitename'] = 'etc'

                news_by_website.setdefault(siteid, [])
                news_by_website.get(siteid).append(item)

        result = news_by_website
    else:
        result = None

    return result
