$(document).ready(function () {
    $(".nav-link").eq(2).addClass("active");

    $("#add-email").click(function () {
        input_name = $("#input-name").val();
        input_email = $("#input-email").val();

        html_email = "\
        <tr class='text-center'> \
            <td scope='row'> \
                <input type='text' class='text-center' style='width:95%;' id='input-name' value='" + input_name + "' disabled readonly> \
            </td> \
            <td scope='row'> \
                <input type='email' class='text-left email-address' style='width:95%;' id='input-email' value='" + input_email + "' disabled readonly> \
            </td> \
            <td scope='row'> \
                <a type='button' class='btn btn-sm btn-danger' style='width:95%;' id='add-email'>삭제</a> \
            </td> \
            </tr> \
        ";

        $("#email-list").append(html_email);

        $("#input-name").val('');
        $("#input-email").val('');
    });
});