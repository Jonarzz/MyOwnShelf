$(document).ready(function () {
    addScrollListener();
    addNavSearchHandler();
});

function addScrollListener() {
    var distanceY = window.pageYOffset || document.documentElement.scrollTop,
        navbar = $("nav"),
        smallNavClass = "nav-small",
        navIcons = $(".nav-inner__icons-container").find(".fa-2x");
    window.addEventListener('scroll', function() {
        distanceY = window.pageYOffset || document.documentElement.scrollTop;
        if (distanceY > 0) {
            if (!navbar.hasClass(smallNavClass)) {
                navbar.addClass(smallNavClass);
                navIcons.removeClass("fa-2x");
                navIcons.addClass("fa-lg");
            }
        } else {
            navbar.removeClass(smallNavClass);
            navIcons.removeClass("fa-lg");
            navIcons.addClass("fa-2x");
        }
    });
}

function addNavSearchHandler() {
    var searchButton = $("#nav-search-button"),
        searchBox = $("#nav-search-box"),
        container = undefined,
        activeContainerClass = "active";

    searchButton.click(function(e) {
        container = $(this).closest(".nav-inner__search-container");
        if (!container.hasClass(activeContainerClass)) {
            container.addClass(activeContainerClass);
            e.preventDefault();
        }
    });

    searchButton.blur(function() {
        setTimeout(function() {
            if (!searchBox.is(":focus")) {
                container.removeClass(activeContainerClass);
                searchBox.val('');
            }
        }, 100);
    });

    searchBox.blur(function() {
        container.removeClass(activeContainerClass);
        searchBox.val('');
    });
}