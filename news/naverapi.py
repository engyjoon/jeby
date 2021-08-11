import json
import re
import time
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


def send_email_by_schedule(current_time=None):
    print('send_email_by_schedule 함수 호출')
    now = datetime.now()

    if current_time is None:
        current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)

    # 사용자별 설정값 조회한다.
    rows = Setting.objects.all()
    for row in rows:
        # 사용자가 설정한 메일 발송 시간 텍스트를 전처리한다.
        times = row.email_send_time.split(';')
        # 함수 호출 시 입력한 시간이 메일 발송 시간에 존재할 경우 처리한다.
        if current_time in times:
            # 함수 호출 시 입력한 시간이 사용자가 설정한 메일 발송 시간 중 몇 번째인지 확인한다.
            index = times.index(current_time)
            # 함수 호출 시 입력한 시간이 사용자가 설정한 메일 발송 시간이 첫번 째에 해당된다면
            # 하루 전 날부터 현재 시간까지 뉴스를 검색하기 위해
            # start_time을 하루 전날 마지막 시간으로 설정한다.
            if index == 0:
                last_time = times[-1].split(':')
                start_time = now.replace(
                    hour=int(last_time[0]), minute=int(last_time[1]), second=0, tzinfo=KST)
                start_time = start_time + timedelta(days=-1)
            # 함수 호출 시 입력한 시간이 사용자가 설정한 메일 발송 시간이 첫번 째에 해당되지 않는다면
            # start_time을 이전 메일 발송 시간으로 설정한다.
            else:
                _time = times[index-1].split(':')
                start_time = now.replace(
                    hour=int(_time[0]), minute=int(_time[1]), second=0, tzinfo=KST)

            # 함수 호출 시 입력한 시간을 end_time으로 설정한다.
            _time = current_time.split(':')
            end_time = now.replace(
                hour=int(_time[0]), minute=int(_time[1]), second=0, tzinfo=KST)
            end_time = end_time + timedelta(seconds=-1)
        # 함수 호출 시 입력한 시간이 메일 발송 시간에 존재하지 않으면 다음 사용자 처리
        else:
            break

        # 사용자가 설정한 메일 수신자들을 조회한다.
        # 사용자 이름은 제외하고 메일주소만 recipients 리스트에 입력한다.
        _recipients = row.email_recipient.split(';')
        recipients = []
        for recipient in _recipients:
            recipients.append(recipient.split(',')[1])

        # 사용자가 설정한 키워드들을 조회한다.
        # 메일 발송 여부가 True인 것만 조회한다.
        keywords = Keyword.objects.filter(author=row.author.id)
        keywords = keywords.filter(mailing=True)

        news = []
        # "메일 발송 시간", "메일 수신자", "키워드"가 존재할 경우에만 뉴스 검색 및 메일 발송을 수행한다.
        if times and recipients and keywords:
            print('times, recipients, keywords 존재')
            # 네이버 검색 API를 사용하여 키워드를 차례로 검색한 후 news 리스트에 입력한다.
            # start_time과 end_time을 인자로 입력하여 end_time부터 start_time까지 조회하도록 한다.
            for keyword in keywords:
                print('get_news_all 함수 호출')
                news = get_news_all(keyword.content, start_time, end_time)

            # 메일 제목을 작성한다.
            # 함수 호출 시 입력한 시간을 사용한다.
            _time = current_time.split(':')
            _now = now.replace(hour=int(_time[0]), minute=int(
                _time[1]), second=0, tzinfo=KST)
            mail_title = f'[Jeby] {_now.year}/{str(_now.month).zfill(2)}/{str(_now.day).zfill(2)} {str(_now.hour).zfill(2)}시 {str(_now.minute).zfill(2)}분 뉴스'

            # 메일 본문을 작성한다.
            _keywords = ', '.join([str(x) for x in keywords])
            mail_content = f'''
                <html>
                    <head>
                        <style>
                            table, th, td {{
                                border: 1px solid #6c757d;
                                border-collapse: collapse;
                            }}

                            th, td {{
                                padding: 5px 10px;
                            }}
                        </style>
                    </head>
                    <body>
                        <h3>Jeby 뉴스 서비스</h3>
                        <p>키워드 : {_keywords}</p>
            '''

            if news:
                mail_content += f'''
                            <table style="width:800px;">
                                <tr style="background-color: #F0F0F0;">
                                    <th style="width:20%;">키워드</th>
                                    <th>기사제목</th>
                                    <th style="width:110px; text-align:center;">발행시간</th>
                                </tr>
                '''

                for new in news:
                    # 뉴스 제목 일정 길이로 자른다.
                    _title = new.get('title')
                    # if len(_title) > 30:
                    #     _title = _title[0:31] + '...'

                    mail_content += f'''
                        <tr>
                            <td>{new.get('keyword')}</td>
                            <td>
                                <a href="{new.get('originallink')}">{_title}</a>
                            </td>
                            <td>{new.get('pubDate').strftime('%Y/%m/%d %H:%M')}</td>
                        </tr>
                    '''

                mail_content += '</table></body></html>'
            else:
                mail_content += f'''
                    <p>검색된 뉴스가 없습니다.</p>
                '''

            # 메일을 발송한다.
            send_mail(
                subject=mail_title,
                message=None,
                html_message=mail_content,
                from_email='jebyhouse@gmail.com',
                recipient_list=recipients,
                fail_silently=False,
            )
            print('메일 발송 완료!!')

            # 네이버 검색 API를 초당 10건으로 제한하고 있기 때문에
            # 1회 메일 발송 후 1초 휴식한다.
            # time.sleep(1)

    return None


def get_news_all(keyword, start_time=None, end_time=None):
    """
    주어진 키워드 사용하여 네이버 검색 API를 끝까지 호출한다.
    start_time과 end_time이 지정될 경우 start_time과 end_time 구간 내 뉴스를 반환한다.
    """

    news = []
    start = 1
    display = 100

    flag = True
    while flag:
        _list = get_news(keyword, display, start, 'date')
        if _list:
            for i in _list:
                # end_time이 존재하고 end_time보다 pubDate가 클 경우 news 리스트에 입력하지 않는다.
                if end_time and end_time < parse(i['pubDate']):
                    continue

                # start_time이 존재하고 start_time보다 뉴스 발행시간이 작을 경우
                # news 리스트에 뉴스 입력을 중지한다.
                if start_time and start_time > parse(i['pubDate']):
                    flag = False
                    break

                i['keyword'] = keyword
                i['pubDate'] = parse(i['pubDate'])

                news.append(i)

            # 검색한 뉴스 개수가 display 개수와 동일할 경우
            # start에 100을 더한 후 다시 뉴스를 검색한다.
            if len(_list) == display:
                start += 100
        else:
            flag = False

    return news


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
