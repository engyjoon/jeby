from datetime import timedelta, datetime, timezone
import json
from dateutil.parser import parse
from django.conf import settings
from django.core.mail import send_mail
from .models import Setting, Keyword
from .naverapi import get_news

KST = timezone(timedelta(hours=9))


def send_email_by_schedule(current_time=None):
    """
    OS Crond가 호출하는 함수이다.
    current_time 매개변수가 없을 경우 datetime.now()를 현재 시간으로 사용한다.
    current_time 매개변수의 "hh:mm" 형식의 문자열이다.
    """
    # current_time 매개변수가 None일 경우
    # 현재 시간을 텍스트로 변환하여 current_time 변수에 저장한다.
    now = datetime.now()
    if current_time is None:
        current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)

    # 사용자 설정값을 조회하여 메일을 발송한다.
    rows = Setting.objects.all()
    for row in rows:
        email_send_time = row.email_send_time
        email_recipient = row.email_recipient

        # 사용자가 설정한 키워드들을 조회한다. 메일 발송 여부가 True인 것만 조회한다.
        keywords = Keyword.objects.filter(author=row.author.id)
        keywords = keywords.filter(mailing=True)

        # 이메일 발송 시간, 이메일 수신자, 키워드가 존재할 경우 아래 내요을 실행한다.
        if email_send_time and email_recipient and keywords:
            # 업무 시간 텍스트를 전처리한다. (시작 시간, 종료 시간)
            work_hour = row.work_hour
            if work_hour is not None:
                _work_hour = row.work_hour.split(';')
                # _work_hour_start = _work_hour[0].split(':')
                _work_hour_end = _work_hour[1].split(':')
                # work_hour_start = now.replace(
                #     hour=int(_work_hour_start[0]), minute=int(_work_hour_start[1]), second=0, tzinfo=KST)
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
                    # work_hour(업무시간)가 설정이되 있지 않다면
                    # start_time을 하루 전날 마지막 시간으로 설정한다.
                    if work_hour is None:
                        last_time = times[-1].split(':')
                        start_time = now.replace(
                            hour=int(last_time[0]), minute=int(last_time[1]), second=0, tzinfo=KST)
                        start_time = start_time + timedelta(days=-1)
                    # work_hour(업무시간)가 설정되어 있다면
                    # start_time을 work_hour 종료 시간 1일 전으로 설정한다.
                    else:
                        start_time = work_hour_end + timedelta(days=-1)

                # 함수 호출 시 입력한 시간이 사용자가 설정한 메일 발송 시간의 첫 번째에 해당되지 않는다면
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

            # 함수 호출 시 입력한 시간이 메일 발송 시간에 존재하지 않으면 다음 사용자를 처리한다.
            else:
                continue

            # 사용자 이름은 제외하고 메일주소만 recipients 리스트에 입력한다.
            _recipients = email_recipient.split(';')
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
            for keyword in keywords:
                news = get_news(keyword.content, start_time, end_time)

                mail_content += f'''
                    <div>
                        <div style="font-size:11pt;"><strong>[{keyword.title}]</strong></div>
                        <div style="font-size:11pt;">
                            검색어 &gt;&gt; {keyword.content}
                        </div>
                '''

                if news:
                    mail_content += f'''
                        <div>
                            <table style="width:850px;">
                                <tr style="background-color:#F0F0F0;">
                                    <th style="width:20%; text-align:center; font-size:11pt;">언론사</th>
                                    <th style="width:68%; text-align:center; font-size:11pt;">기사제목</th>
                                    <th style="width:12%; text-align:center; font-size:11pt;">발행시간</th>
                                </tr>
                    '''

                    for new in news:
                        sitename = new.get('sitename')
                        if sitename == 'unknown':
                            sitename = '-'

                        mail_content += f'''
                            <tr>
                                <td style="font-size:11pt; text-align:center;">{sitename}</td>
                                <td style="font-size:11pt;">
                                    <a href="{new.get('originallink')}">{new.get('title')}</a>
                                </td>
                                <td style="font-size:11pt; text-align:center;">{new.get('pubDate').strftime('%m/%d %H:%M')}</td>
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
 

def send_email_by_share(data):
    """
    뉴스 공유 버튼을 선택하면 실행되는 함수이다.
    """
    # 검색 키워드
    keyword = data.get('keyword')
    # 이메일 수신자
    recipient = [data.get('recipient')]
    # 이메일 제목
    title = data.get('title')
    # 이메일 메시지
    message = data.get('message').replace('\n','<br>')
    # 공유 뉴스
    news = json.loads(data.get('news'))

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
                <div style="font-size:11pt; padding-bottom:0px; margin-bottom:5px;">{message}</div>
                <br>
                <div>
                    <div style="font-size:11pt;">
                        검색어 &gt;&gt; {keyword}
                    </div>
                    <div>
                        <table style="width:850px;">
                            <tr style="background-color:#F0F0F0;">
                                <th style="width:20%; text-align:center; font-size:11pt;">언론사</th>
                                <th style="width:68%; text-align:center; font-size:11pt;">기사제목</th>
                                <th style="width:12%; text-align:center; font-size:11pt;">발행시간</th>
                            </tr>
    '''

    for new in news:
        mail_content += f'''
                <tr>
                    <td style="font-size:11pt; text-align:center;">{new.get('site_name')}</td>
                    <td style="font-size:11pt;">
                        <a href="{new.get('news_link')}">{new.get('news_title')}</a>
                    </td>
                    <td style="font-size:11pt; text-align:center;">{parse(new.get('news_date')).strftime('%m/%d %H:%M')}</td>
                </tr>
            '''

    mail_content += '''
                </table>
            </div>
        </div>
        <br><br>
    '''

    mail_content += f'''
                <div>
                    <a href="{settings.SERVICE_URL}" target="_blank">{settings.SERVICE_URL}</a> (크롬 브라우저 사용 권장)
                </div>
            </body>
        </html>
    '''

    # 메일을 발송한다.
    send_mail(
        subject=title,
        message=None,
        html_message=mail_content,
        from_email='jebyhouse@gmail.com',
        recipient_list=recipient,
        fail_silently=False,
    )
