var template = {}

template.taglist = Handlebars.compile('    <ul>\
        {{#each tags}}\
        <li>\
            <a href="/tag/{{ this.id }}">\
                {{ this.name }}\
            </a>\
            <span class="tagcount">{{ this.count }}</span>\
        </li>\
        {{/each }}\
    </ul>'
    );

template.popup = Handlebars.compile('<div class="popup">\
                <div class="close"><span>[X]</span></div>\
                <div class="thumbspop">\
                {{#each thumbs }}\
                    <img src="{{ this }}">\
                {{/each}}\
                </div>\
                <div class="movinfo">\
                    <div class="movietags">Tags:\
                        {{#each tags}}\
                            <span class="atag">{{this.name }}</span>\
                        {{/each}}\
                    </div>\
                    <div class="addtag">\
                        Add tag: <input id="addtag-{{id}}" data-url="{{tagurl}}" data-info="{{url}}" class="addtaginput"> <input type="button" class="addtagbutton" data-id="{{id}}" value="Add">\
                    </div>\
                    <div class="moviepath">\
                        {{ this.path }}\
                    </div>\
                </div>\
            </div>'
            );
    
function addtag(obj) {
    var tag = obj.val();
    var url = obj.data("url");
    var info = obj.data("info");
    $.post(url, {"tag": tag},function() {
        obj.val("");
        load_taglist();
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
        $(".popup").remove();
        var html = template.popup(data);
        var t = $("#movie-"+data.id);
        var pop = t.find(".popupc");
        pop.html(html);
        run_hooks();
        pop.click(function (e) {e.stopImmediatePropagation();});
        pop.find(".close").click(function (event) {
            event.stopImmediatePropagation();
            pop.empty();
        });
    });
}

function load_taglist() {
    $.get("/tags/", function (data) {
        $("#tlinner").html(template.taglist(data));
    });
}

function run_hooks() {
    $(".playvideobutton").click(function () {
        var t = $(this);
        var id = t.data("id");
        $.get("/run/"+id);
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
    load_taglist();
    $(".mainthumb").click(function () {
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