var template = {}

template.thumbs = Handlebars.compile('<div class="thumbspop">\
                {{#each thumbs }}\
                    <img src="{{ this }}">\
                {{/each}}\
                </div>');
template.tags = Handlebars.compile('<div class="movietags">Tags:\
                        {{#each tags}}\
                            <span class="atag">{{this.name }}</span>\
                        {{/each}}\
                    </div>');
    
function addtag(obj) {
    var tag = obj.val();
    var url = obj.data("url");
    var info = obj.data("info");
    $.post(url, {"tag": tag},function() {
        obj.val("");
        show_popup(info);
    });
}

function complete_tags(inputfield) {
    var value = inputfield.val();
    $(".popcomplete").remove();
    var pos = inputfield.offset();
    var container = $("<div/>").addClass("popcomplete");
    container.css({
        "top":pos.top + inputfield.outerHeight(),
        "left": pos.left,
        "position": "absolute"
    });
    $("body").append(container);
    container.click(function () {container.remove();});
    $.get("/movies/tags/startswith/" + value, function(data) {
        var ul = $("<ul/>");
        container.append(ul);
        $.each(data, function(i, v) {
            var li = $("<li/>");
            li.text(v.name);
            ul.append(li);
            li.click(function () {
                inputfield.val(v.name);
                addtag(inputfield);
            });
        });
    });
}

function show_popup(movieurl) {
    $.get(movieurl, function (data) {
        $(".infodata").hide();
        var thumbs = template.thumbs(data);
        var tags = template.tags(data);
        
        var t = $("#movie-"+data.id);
        var info = t.find(".infodata");
        info.find(".thumbsholder").html(thumbs);
        info.find(".tagsholder").html(tags);
        //run_hooks();
        info.show();
        //pop.click(function (e) {e.stopImmediatePropagation();});
        
        info.find(".close").click(function (event) {
            event.stopImmediatePropagation();
            info.hide();
        });
    });
}


function run_hooks() {
    $(".playvideobutton").click(function (e) {
        var t = $(this);
        var id = t.prop("href");
        $.get(id);
        e.preventDefault();
        return false;
    });
    $("input.addtaginput").keyup(function (event) {
        var t = $(this);
        complete_tags(t);
    });
    $("input.addtaginput").keydown(function (event) {
        var t = $(this);
        if ( event.which == 13 ) {
            addtag(t);
        }
    });
    $("input.addtagbutton").click(function () {
        var t = $(this);
        var id = t.data("id");
        var t2 = $("#addtag-"+id);
        addtag(t2);
    });
}

$(document).ready(function () {
    $(".showpopup").click(function () {
        var t = $(this);
        show_popup(t.data("url"));
    });
    $("#search").keydown(function(e) {
        if (e.which == 13) {
            e.preventDefault();
            var url = "/search/" + $("#search").val();
            window.open(url, "_self");
        }
    });
    
    $("#pages").click(function () {
        $("#pageslist").toggle();
    });
    run_hooks();
});