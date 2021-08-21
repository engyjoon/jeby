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

    $("#siteEditModal").on('show.bs.modal', function(event) {
        var data = $(event.relatedTarget).data('siteuri');
        $("#modal-siteuri").val(data);
        $("#modal-sitedesc").val('');
    });

    $("#siteEditModal").on('shown.bs.modal', function(event) {
        $("#modal-sitedesc").focus();
    });
});