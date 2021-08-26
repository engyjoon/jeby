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
        var actionurl = $(event.relatedTarget).data('action-url');
        var actiontype = $(event.relatedTarget).data('action-type');

        $("#modal-siteuri").val(siteuri);
        $("#modal-sitedesc").val(sitename);
        $("#frmSiteEditModeal").attr("action", actionurl);

        console.log(actionurl);

        if (actiontype === 'create') {
            $("#frmSiteEditModeal").attr("method", "POST");
        } else if (actiontype === 'update') {
            $("#frmSiteEditModeal").attr("method", "PUT");
        }
    });

    $("#siteEditModal").on('shown.bs.modal', function (event) {
        $("#modal-sitedesc").focus();
    });

    $("#btnSaveSiteEditModal").click(function () {
        const csrftoken = getCookie('csrftoken');

        let url = $("#frmSiteEditModeal").attr("action");
        let method = $("#frmSiteEditModeal").attr("method");

        let headers = {
            'X-CSRFToken': csrftoken
        }

        let data = {
            address: $("#modal-siteuri").val(),
            description: $("#modal-sitedesc").val()
        }

        $.ajax({
            method: method,
            url: url,
            headers: headers,
            data: data,
            dataType: "json"
        })
            .done(function () {
                $("#siteEditModal").modal('hide');
                $("#frm-search").submit();
            })
            .fail(function () {
                console.log("fail!")
            });
    });

    $(".check-sitename").click(function () {
        target = $(this).children();
        if (target.hasClass("bi-square")) {
            target.removeClass("bi-square");
            target.addClass("bi-check-square");
        } else {
            target.removeClass("bi-check-square");
            target.addClass("bi-square");
        }
    })
});