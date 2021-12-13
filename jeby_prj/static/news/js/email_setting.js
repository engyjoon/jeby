$(document).ready(function () {
    html_email = "\
        <tr class='text-center'> \
            <td scope='row'> \
                <input type='email' class='form-control form-control-sm email-address' style='width:100%;' \
                value='#input_email#' data-recipient='#recipient#' disabled readonly> \
            </td> \
            <td scope='row'> \
                <a type='button' class='btn btn-sm btn-danger btn-remove-email' style='width:95%;'>삭제</a> \
            </td> \
        </tr> \
    ";

    // 이메일 설정 메뉴 활성화시킨다.
    $(".nav-link").eq(3).addClass("active");

    // 이메일 발송 시간을 표시한다.
    if (email_send_times !== 'None') {
        email_send_times = email_send_times.split(';');
        for (i in email_send_times) {
            $("#send-time .hour").each(function (index) {
                if (email_send_times[i] === $(this).data('hour')) {
                    $(this).addClass("time-active");
                }
            });
        }
    }

    // 업무 시간을 표시한다.
    if (work_hour !== 'None') {
        work_hour = work_hour.split(';');
        $("#workTimeStart").val(work_hour[0]);
        $("#workTimeEnd").val(work_hour[1]);
    }

    // 이메일 수신자 추가 버튼을 선택하면 실행한다.
    $("#add-email").click(function () {
        selected_email = $("#selectRecipient option:selected").html();
        selected_value = $("#selectRecipient option:selected").val();
        html_result = html_email.replace('#input_email#', selected_email).replace('#recipient#', selected_value);

        $("#email-list").append(html_result);
        $("#selectRecipient option:eq(0)").prop("selected", true);
    });

    // 이메일 수신자 삭제 버튼을 선택하면 실행한다.
    // append 메소드로 동적으로 추가된 요소에 click 이벤트를 설정한다.
    // 동적으로 이벤트를 설정할 때는 on 메소드를 사용해야 한다.
    // 첫 번째 선택 요소는 동적으로 추가된 요소가 아니어야 한다. (#email-list)
    $("#email-list").on('click', '.btn-remove-email', function () {
        $(this).parent().parent().detach();
    });

    // 이메일 발송 시간을 선택하면 활성화시킨다.
    $("#send-time .hour").click(function () {
        $(this).toggleClass("time-active");
    });

    // 이메일 설정 페이지 수정 버튼을 선택하면 아래 내용이 실행된다.
    $("#btnApplySendTime").click(function () {
        var activeTimes = new Array();
        $(".time-active").each(function (idx) {
            activeTimes[idx] = $(this).html()
        });

        var workTimeStart = $("#workTimeStart").val();
        var workTimeEnd = $("#workTimeEnd").val();
        var workTime = "";
        if (workTimeStart !== "" && workTimeEnd !== "") {
            workTime = workTimeStart + ";" + workTimeEnd;
        }

        var emailAddresses = new Array();
        $(".email-address").each(function (idx) {
            emailAddresses[idx] = $(this).data('recipient');
        });

        $("#frmMain [name='email_send_time']").val(activeTimes.join(";"));
        $("#frmMain [name='work_hour']").val(workTime);
        $("#frmMain [name='email_recipients_str']").val(emailAddresses.join(";"));
        $("#frmMain").submit();
    })
});