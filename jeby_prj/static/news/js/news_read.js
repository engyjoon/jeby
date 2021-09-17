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

    // 화면 오픈 시 검색창에 커서를 이동시킨다.
    // 커서를 검색어 마지막에 위치시킨다.
    _keyword = $("#input-keyword").val();
    $("#input-keyword").focus();
    $("#input-keyword").val('').val(_keyword);

    // 검색버튼을 선택하면 검색을 수행한다.
    $("#search-img").click(function () {
        $("#frm-search").submit();
    });

    // 미리 입력한 키워드 리스트에서 키워드를 선택하면
    // 키워드가 검색창에 표시되고 키워드 리스트 모달을 닫는다.
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

    // 뉴스를 선택/해제할 때마다 수행하는 내용이다.
    $(".check-sitename").click(function () {
        // 선택/해제한 뉴스 정보를 변수에 저장한다.
        news_sitename = $(this).parent().find('span').eq(1).children().data('sitename');
        news_title = $.trim($(this).parent().find('a').eq(1).children().html());
        news_link = $.trim($(this).parent().find('a').eq(1).attr('href'));
        news_date = $.trim($(this).parent().find('span').eq(3).html());
        news_id = $(this).parent().attr('id');

        // 언론사명이 없을 경우 대시를 입력한다.
        if (news_sitename === '') {
            news_sitename = '-';
        }

        // 뉴스 선택 시 선택 Card에 삽입할 뉴스 포맷을 미리 생성한다.
        html = '' +
            '<div class="news-item-selected fs-6" data-newsid="' + news_id + '"' + 
                'id="selected-' + news_id + '"> ' +
            '   <span class="checked-sitename me-2"> ' +
            '       <i class="bi bi-check-square"></i> ' +
            '   </span> ' +
            '   <span class="box-sitename me-2"> ' + news_sitename + '</span> ' +
            '   <span class="news-title" style="font-weight:400;">' + 
                    '<a href="' + news_link + '" target="_blank">' + news_title + '</a>' +
                '</span>' +
                '<span class="badge bg-light text-dark">' + news_date + '</span>' +
            '</div>';

        checkbox = $(this).children();
        // 뉴스를 선택할 경우 수행하는 내용이다.
        if (checkbox.hasClass("bi-square")) {
            checkbox.removeClass("bi-square");
            checkbox.addClass("bi-check-square");

            $("#selectedNewsBody").append(html);
        // 뉴스를 해제할 경우 수행하는 내용이다.
        } else {
            checkbox.removeClass("bi-check-square");
            checkbox.addClass("bi-square");

            $("#selected-"+news_id).detach();
        }

        // 선택한 뉴스 개수에 따라 선택 뉴스 Card 출력/미출력
        applySelectedNews();
    });

    // 선택한 뉴스의 체크박스를 선택했을 때 수행하는 내용이다.
    // append 메소드로 동적으로 추가된 요소에 click 이벤트를 설정한다.
    // 동적으로 이벤트를 설정할 때는 on 메소드를 사용해야 한다.
    // 첫 번째 선택 요소는 동적으로 추가된 요소가 아니어야 한다. (#selectedNewsBody)
    $("#selectedNewsBody").on('click', '.checked-sitename', function () {
        // 선택한 뉴스의 체크박스를 해제할 경우 해당 뉴스를 선택 Card에서 제거한다.
        $(this).parent().detach();

        news_id = $(this).parent().data('newsid');
        
        // 체크박스 이미지 박스 이미지로 변경한다.
        checkbox = $("#"+news_id).find("i");
        checkbox.removeClass("bi-check-square");
        checkbox.addClass("bi-square");

        // 선택한 뉴스 개수에 따라 선택 뉴스 Card 출력/미출력
        applySelectedNews();
    });

    // 뉴스를 선택/해제할 때마다 수행할 함수이다.
    // 선택한 뉴스 개수를 업데이트하고 선택한 뉴스가 0개일 경우
    // 선택뉴스 Card를 숨긴다.
    function applySelectedNews() {
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
    }

    // 뉴스 선택 후 공유하기 링크를 선택했을 때
    // 나타나는 모달을 초기화한다.
    $("#shareNewsModal").on('show.bs.modal', function (event) {
        // 첫 번째 option에 value 설정이 존재해야 아래 코드가 정상 수행된다.
        $("#selectRecipient option:eq(0)").prop("selected", true);
        $("#message-text").val("");
        $("#shareNewsModalMessage").css('display', 'none');
        $("#spinnerEmail").css('display', 'none');
    });

    // 뉴스 공유하기 버튼 선택 시 REST API를 호출한다.
    $("#btnShareNewsModal").click(function () {
        const csrftoken = getCookie('csrftoken');

        let headers = {
            'X-CSRFToken': csrftoken
        }

        let arr_news = [];
        $selected_news = $("#selectedNewsBody").children();
        $selected_news.each(function(index) {
            arr_news[index] = {
                'site_name': $.trim($(this).children().eq(1).text()),
                'news_title': $.trim($(this).children().eq(2).children().text()),
                'news_link': $.trim($(this).children().eq(2).children().attr('href')),
                'news_date': $.trim($(this).children().eq(3).text())
            }
        });

        let keyword = $("#input-keyword").val();
        let recipient = $("#selectRecipient").val();
        let title = $("#message-title").val();
        let message = $("#message-text").val();

        // 수신자를 선택하지 않을 경우 경보를 발생시킨다.
        if (recipient === '') {
            $("#shareNewsModalMessage").html('수신자를 선택해주세요.');
            $("#shareNewsModalMessage").removeClass('alert-primary').addClass('alert-danger');
            $("#shareNewsModalMessage").css('display', 'block');
        // 제목을 선택하지 않을 경우 경보를 발생시킨다.
        } else if (title === '') {
            $("#shareNewsModalMessage").html('제목을 선택해주세요.');
            $("#shareNewsModalMessage").removeClass('alert-primary').addClass('alert-danger');
            $("#shareNewsModalMessage").css('display', 'block');
        } else {
            let data = {
                keyword: keyword,
                recipient: recipient,
                title : title,
                message: message,
                news: JSON.stringify(arr_news)
            }
            
            $.ajax({
                method: "POST",
                url: $("#frmShareNewsModal").attr("action"),
                headers: headers,
                data: data,
                dataType: "json",
                beforeSend: function (xhr) {
                    $("#spinnerEmail").css('display', 'block');
                },
                complete: function (xhr) {
                    $("#spinnerEmail").css('display', 'none');
                }
            })
                .done(function (result) {
                    // console.log(result);
                    // $("#shareNewsModal").modal('hide');
                    $("#shareNewsModalMessage").html('공유를 완료하였습니다.');
                    $("#shareNewsModalMessage").removeClass('alert-danger').addClass('alert-primary');
                    $("#shareNewsModalMessage").css('display', 'block');
                })
                .fail(function () {
                    console.log("fail!");
                });
        }
    });

    $("#btnShareNewsModal").on('hide.bs.modal', function (event) {
        $("#shareNewsModalMessage").removeClass('alert-primary');
        $("#shareNewsModalMessage").removeClass('alert-danger');
    });
});