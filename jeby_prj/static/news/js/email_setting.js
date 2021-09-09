$(document).ready(function () {
    html_email = "\
        <tr class='text-center'> \
            <td scope='row'> \
                <input type='text' class='text-center' style='width:95%;' value='#input_name#' disabled readonly> \
            </td> \
            <td scope='row'> \
                <input type='email' class='text-left email-address' style='width:95%;' value='#input_email#' disabled readonly> \
            </td> \
            <td scope='row'> \
                <a type='button' class='btn btn-sm btn-danger' style='width:95%;'>삭제</a> \
            </td> \
        </tr> \
    ";

    $(".nav-link").eq(3).addClass("active");

    if (email_send_times != 'None') {
        email_send_times = email_send_times.split(';');
        for (i in email_send_times) {
            $("#send-time .hour").each(function (index) {
                if (email_send_times[i] === $(this).data('hour')) {
                    $(this).addClass("time-active");
                }
            });
        }
    }

    if (email_recipients != 'None') {
        email_recipients = email_recipients.split(';');
        for (i in email_recipients) {
            email_recipient = email_recipients[i].split(',');
            recipient_name = email_recipient[0];
            recipient_email = email_recipient[1];

            html_result = html_email.replace('#input_name#', recipient_name).replace('#input_email#', recipient_email);

            $("#email-list").append(html_result);
        }
    }

    $("#add-email").click(function () {
        input_name = $("#input-name").val();
        input_email = $("#input-email").val();

        html_result = html_email.replace('#input_name#', input_name).replace('#input_email#', input_email);

        $("#email-list").append(html_result);

        $("#input-name").val('');
        $("#input-email").val('');
    });

    $("#send-time .hour").click(function () {
        $(this).toggleClass("time-active");
    });
});