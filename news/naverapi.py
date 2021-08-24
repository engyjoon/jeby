import json
import re
from time import sleep
from datetime import time, timedelta, datetime, timezone
import urllib.request
import urllib.parse
from dateutil.parser import parse
from django.conf import settings
from django.core.mail import send_mail
from .models import Setting, Keyword, Site


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


def send_email_by_schedule(current_time=None):
    """
    OS Crond가 호출하는 함수이다.
    current_time 매개변수가 없을 경우 datetime.now()를 현재 시간으로 사용한다.
    current_time 매개변수의 "hh:mm" 형식의 문자열이다.
    """

    now = datetime.now()
    if current_time is None:
        current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)

    # 사용자별 설정값을 조회한다.
    rows = Setting.objects.all()
    for row in rows:
        email_send_time = row.email_send_time
        email_recipient = row.email_recipient

        # 사용자가 설정한 키워드들을 조회한다. 메일 발송 여부가 True인 것만 조회한다.
        keywords = Keyword.objects.filter(author=row.author.id)
        keywords = keywords.filter(mailing=True)

        if email_send_time and email_recipient and keywords:
            # 업무 시간 텍스트를 전처리한다. (시작 시간, 종료 시간)
            work_hour = row.work_hour
            if work_hour is not None:
                _work_hour = row.work_hour.split(';')
                _work_hour_start = _work_hour[0].split(':')
                _work_hour_end = _work_hour[1].split(':')
                work_hour_start = now.replace(
                    hour=int(_work_hour_start[0]), minute=int(_work_hour_start[1]), second=0, tzinfo=KST)
                work_hour_end = now.replace(
                    hour=int(_work_hour_end[0]), minute=int(_work_hour_end[1]), second=0, tzinfo=KST)

            # 사용자가 설정한 메일 발송 시간 텍스트를 전처리한다.
            times = row.email_send_time.split(';')
            # 함수 호출 시 입력한 시간이 메일 발송 시간에 존재할 경우 처리한다.
            if current_time in times:
                # 함수 호출 시 입력한 시간이 사용자가 설정한 메일 발송 시간 중 몇 번째인지 확인한다.
                index = times.index(current_time)
                # 함수 호출 시 입력한 시간이 사용자가 설정한 메일 발송 시간 중 첫 번째에 해당되고
                if index == 0:
                    # work_hour가 설정이되 있지 않다면
                    # start_time을 하루 전날 마지막 시간으로 설정한다.
                    if work_hour is None:
                        last_time = times[-1].split(':')
                        start_time = now.replace(
                            hour=int(last_time[0]), minute=int(last_time[1]), second=0, tzinfo=KST)
                        start_time = start_time + timedelta(days=-1)
                    # work_hour가 설정되어 있다면
                    # start_time을 work_hour 종료 시간 1일 전으로 설정한다.
                    else:
                        start_time = work_hour_end + timedelta(days=-1)

                # 함수 호출 시 입력한 시간이 사용자가 설정한 메일 발송 시간이 첫 번째에 해당되지 않는다면
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

                print('start_time:', start_time)
                print('end_time:', end_time)
            # 함수 호출 시 입력한 시간이 메일 발송 시간에 존재하지 않으면 다음 사용자 처리
            else:
                continue

            # 사용자가 설정한 메일 수신자들을 조회한다.
            # 사용자 이름은 제외하고 메일주소만 recipients 리스트에 입력한다.
            _recipients = row.email_recipient.split(';')
            recipients = []
            for recipient in _recipients:
                recipients.append(recipient.split(',')[1])

            # 메일 제목을 작성한다.
            # 함수 호출 시 입력한 시간을 사용한다.
            _time = current_time.split(':')
            _now = now.replace(hour=int(_time[0]), minute=int(
                _time[1]), second=0, tzinfo=KST)
            mail_title = f'[공유] {_now.year}/{str(_now.month).zfill(2)}/{str(_now.day).zfill(2)} {str(_now.hour).zfill(2)}시 {str(_now.minute).zfill(2)}분 뉴스'

            # 메일 본문을 작성한다.
            mail_content = f'''
                <html>
                    <head>
                        <style>
                            body {{
                                font-family: 'Malgun Gothic';
                                font-size: 11pt;
                            }}

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
                        <div style="font-weight:bold; font-size:18pt; padding-bottom:0px; margin-bottom:5px;">
                            {settings.EMAIL_TITLE}
                        </div>
                        <div>
                            <a href="{settings.SERVICE_URL}" target="_blank">{settings.SERVICE_URL}</a> (크롬 브라우저 사용 권장)
                        </div>
                        <br><br>
            '''

            # 네이버 검색 API를 사용하여 키워드를 차례로 검색한 후 news 리스트에 입력한다.
            # start_time과 end_time을 인자로 입력하여 end_time부터 start_time까지 조회하도록 한다.
            news = []
            for keyword in keywords:
                news = get_news(keyword.content, start_time, end_time)

                mail_content += f'''
                    <div>
                        <div><strong>[{keyword.title}]</strong></div>
                        <div>
                            검색어 &gt;&gt; {keyword.content}
                        </div>
                '''

                if news:
                    mail_content += f'''
                        <div>
                            <table style="width:750px;">
                                <tr style="background-color: #F0F0F0;">
                                    <th style="width:85%; text-align:center;">기사제목</th>
                                    <th style="width:15%; text-align:center;">발행시간</th>
                                </tr>
                    '''

                    for new in news:
                        mail_content += f'''
                            <tr>
                                <td><a href="{new.get('originallink')}">{new.get('title')}</a></td>
                                <td style="text-align:center;">{new.get('pubDate').strftime('%m/%d %H:%M')}</td>
                            </tr>
                        '''

                    mail_content += '''
                                </table>
                            </div>
                        </div>
                        <br><br>
                    '''
                else:
                    mail_content += f'''
                        <p>검색된 뉴스가 없습니다.</p>
                        <br>
                '''

            mail_content += f'''
                    </body>
                </html>
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

    return None


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
