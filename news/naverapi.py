import json
import re
from datetime import timedelta, datetime, timezone
import urllib.request
import urllib.parse
from dateutil.parser import parse
from django.conf import settings
from .models import Site


KST = timezone(timedelta(hours=9))


def get_news_by_hour(keyword, start_hour: int = 24, end_hour: int = 0):
    """
    주어진 매개변수 시간만큼 최근 뉴스 리스트를 반환한다.
    start_hour와 end_hour를 int 형식으로 받아 datetime 형식으로 변환한다.
    """

    now = datetime.now()
    end_time = now.replace(tzinfo=KST) + timedelta(hours=-end_hour)
    start_time = end_time + timedelta(hours=-start_hour)

    # 현재부터 24시간 이전까지 뉴스를 조회한다.
    result = get_news(keyword, start_time, end_time)

    return result


def get_news(keyword, start_time: datetime = None, end_time: datetime = None):
    """
    주어진 키워드 사용하여 네이버 검색 API를 끝까지 호출한다.
    start_time과 end_time이 지정될 경우 start_time과 end_time 구간 내 뉴스를 반환한다.
    """

    start = 1
    display = 100

    sites = Site.objects.all()

    news = []
    flag = True
    while flag:
        _list = call_naverapi(keyword, display, start, 'date')
        if _list:
            for i in _list:
                # end_time이 존재하고 end_time보다 pubDate가 클 경우
                # news 리스트에 입력하지 않는다.
                if end_time and end_time < parse(i['pubDate']):
                    continue

                # start_time이 존재하고 start_time보다 뉴스 발행시간이 작을 경우
                # news 리스트에 뉴스 입력을 중지한다.
                if start_time and start_time > parse(i['pubDate']):
                    flag = False
                    break

                # 개별 뉴스에 키워드를 입력한다.
                i['keyword'] = keyword

                # 개별 뉴스의 발행시간을 datetime 형식으로 변환하여 다시 입력한다.
                i['pubDate'] = parse(i['pubDate'])

                # 개별 뉴스에서 언론사 URI를 추출한다.
                pattern = re.compile(r'^https?://([\w.-]*).*')
                if i.get('originallink'):
                    website = pattern.search(i.get('originallink'))
                else:
                    website = pattern.search(i.get('link'))
                    i['originallink'] = i.get('link')

                # 개별 뉴스에 언론사 정보를 입력한다.
                if website is not None:
                    uri = website.group(1)
                    i['siteuri'] = uri

                    try:
                        i['sitename'] = sites.get(address=uri)
                        i['siteid'] = sites.get(address=uri).pk
                    except Site.DoesNotExist:
                        i['sitename'] = 'unknown'
                else:
                    print('URI 추출 실패')
                    print(f'originallink : {i.get("originallink")}')
                    print(f'link : {i.get("link")}')

                news.append(i)

            # 검색한 뉴스 개수가 display 개수와 동일할 경우
            # start에 100을 더한 후 다시 뉴스를 검색한다.
            if len(_list) == display:
                start += 100
                if start > 1000:
                    break
            else:
                break
        else:
            flag = False

        # 네이버 검색 API를 초당 10건으로 제한하고 있기 때문에
        # HTTP 상태코드 429 (초당 호출 한도 초과 오류)
        # 1회 메일 발송 후 일정 시간 동안 휴식한다.
        # sleep(0.5)

    return news


def call_naverapi(keyword, display, start, sort):
    """
    네이버 뉴스 API 호출 및 결과 반환
    """

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
