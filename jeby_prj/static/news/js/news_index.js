$(document).ready(function () {
    $(".nav-link").eq(0).addClass("active");

    $("#search-img").click(function () {
        $("#frm-search").submit();
    });
});