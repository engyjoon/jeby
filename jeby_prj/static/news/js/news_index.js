$(document).ready(function () {
    $(".nav-link").eq(0).addClass("active");

    $("#search-img").click(function () {
        $("#frm-search").submit();
    });

    $(".btn-select-keyword").click(function () {
        // console.log($(this).data("id"));
        $("#input-keyword").val($(this).data("keyword"));
        $("#keywordListModal").modal('hide');
    });
});