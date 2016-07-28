$(document).ready(function () {
    setFeedPostSize();
});

function setFeedPostSize() {
    $(".feed-post__side").each(function() {
        $(this).height($(this).prev().height());
    });
}