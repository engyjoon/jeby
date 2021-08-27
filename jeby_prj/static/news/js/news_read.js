// 검색창에 키워드가 없으면 검색창 위치를 중간으로 변경한다.
if ($("#input-keyword").val() == '') {
    $("#search-box").addClass("d-flex align-items-center h-50");
    $("#search-box").children().addClass("w-100");
}

// 선택뉴스 개수가 0개이면 선택뉴스 card를 숨긴다.
if ($(".check-sitename .bi-check-square").length === 0) {
    $("#selectedNews").hide();
}

// Ajax를 사용해 rest api 호출 시 csrftoken을 얻기 위해 사용한다.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {
    // 네비게이션바에서 해당 메뉴를 활성화한다.
    $(".nav-link").eq(0).addClass("active");

    // 검색버튼을 선택하면 검색을 수행한다.
    $("#search-img").click(function () {
        $("#frm-search").submit();
    });

    // 미리 입력한 키워드 리스트에서 키워드를 선택하면
    // 키워드가 검색창에 표시되고 키워드 리스트 모달이 닫힌다.
    $(".btn-select-keyword").click(function () {
        $("#input-keyword").val($(this).data("keyword"));
        $("#keywordListModal").modal('hide');
    });

    // 언론사 수정 기능 사용 시 해당 모달에 선택한 언론사 정보가 전달되도록 한다.
    $("#siteEditModal").on('show.bs.modal', function (event) {
        var siteuri = $(event.relatedTarget).data('siteuri');
        var sitename = $(event.relatedTarget).data('sitename');
        var actionurl = $(event.relatedTarget).data('action-url');
        var actiontype = $(event.relatedTarget).data('action-type');

        $("#modal-siteuri").val(siteuri);
        $("#modal-sitedesc").val(sitename);
        $("#frmSiteEditModeal").attr("action", actionurl);

        // 언론사가 존재하지 않을 경우 method를 POST로 설정하고
        // 언론사가 존재할 경우 method를 PUT으로 설정한다.
        if (actiontype === 'create') {
            $("#frmSiteEditModeal").attr("method", "POST");
        } else if (actiontype === 'update') {
            $("#frmSiteEditModeal").attr("method", "PUT");
        }
    });

    // 언론사 수정 모달이 보여진 후 언론사명 입력공간에 포커스를 옮긴다.
    $("#siteEditModal").on('shown.bs.modal', function (event) {
        $("#modal-sitedesc").focus();
    });

    // 언론사 수정 버튼 선택 시 REST API를 호출한다.
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

    // 뉴스를 선택할 때마다 수행하는 내용이다.
    $(".check-sitename").click(function () {
        // 뉴스를 체크박스 이미지를 toggling한다.
        target = $(this).children();
        if (target.hasClass("bi-square")) {
            target.removeClass("bi-square");
            target.addClass("bi-check-square");
        } else {
            target.removeClass("bi-check-square");
            target.addClass("bi-square");
        }

        // 선택뉴스 개수를 저장한다.
        total_count = $(".check-sitename .bi-check-square").length;

        // 선택뉴스 개수를 선택뉴스 card header에 표시한다.
        $("#selectedCount").html(total_count);

        // 선택뉴스 개수가 1개 이상일 경우 선택뉴스 card를 보여주고
        // 선택뉴스 개수가 0개일 경우 선택뉴스 card를 숨긴다.
        if (total_count > 0) {
            $("#selectedNews").show();
        } else {
            $("#selectedNews").hide();
        }

        news_sitename = $(this).parent().find('span').eq(1).children().data('sitename');
        news_title = $.trim($(this).parent().find('a').children().eq(0).html());
        news_date = $.trim($(this).parent().find('a').children().eq(1).html());

        html = '' +
            '<div class="news-item-selected fs-6"> ' +
            '   <span class="check-sitename me-2"> ' +
            '       <i class="bi bi-check-square"></i> ' +
            '   </span> ' +
            '   <span class="box-sitename me-2"> ' + news_sitename + '</span> ' +
            '</div>';
        console.log(html);
    });
});