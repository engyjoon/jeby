import json
import urllib.request
import urllib.parse
from django.conf import settings


def get_news(keyword):
    """네이버 뉴스 API 호출 및 결과 반환"""

    values = {
        'query': urllib.parse.quote(keyword),
        'display': 10,
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
        result = json.loads(response_body.decode('utf-8')).get('items')
    else:
        result = None

    return result
