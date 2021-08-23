function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {
    $(".nav-link").eq(0).addClass("active");

    $("#search-img").click(function () {
        $("#frm-search").submit();
    });

    $(".btn-select-keyword").click(function () {
        $("#input-keyword").val($(this).data("keyword"));
        $("#keywordListModal").modal('hide');
    });

    if ($("#input-keyword").val() == '') {
        $("#search-box").addClass("d-flex align-items-center h-50");
        $("#search-box").children().addClass("w-100");
    }

    $("#siteEditModal").on('show.bs.modal', function (event) {
        var siteuri = $(event.relatedTarget).data('siteuri');
        var sitename = $(event.relatedTarget).data('sitename');
        var action = $(event.relatedTarget).data('action');
        $("#modal-siteuri").val(siteuri);
        $("#modal-sitedesc").val(sitename);
        $("#frmSiteEditModeal").attr("action", action)
    });

    $("#siteEditModal").on('shown.bs.modal', function (event) {
        $("#modal-sitedesc").focus();
    });

    $("#btnSaveSiteEditModal").click(function () {
        const csrftoken = getCookie('csrftoken');

        let url = $("#frmSiteEditModeal").attr("action");

        let headers = {
            'X-CSRFToken': csrftoken
        }

        let data = {
            address: $("#modal-siteuri").val(),
            description: $("#modal-sitedesc").val()
        }

        console.log(url);
        console.log(headers);
        console.log(data);

        $.ajax({
            method: 'POST',
            url: url,
            headers: headers,
            data: data,
            dataType: "json"
        })
            .done(function (msg) {
                console.log(msg)
            });
    });
});