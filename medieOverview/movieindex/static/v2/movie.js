var template = {}

template.video = Handlebars.compile('\ <div id="playvideo">\
                        <video width="320" height="240" controls>\
                            <source id="" src="{{ download_url }}"/>\
                        </video>\
                    </div>');

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
    
function addtag(obj, nopopup) {
    var tag = obj.val();
    var url = obj.data("url");
    var info = obj.data("info");
    $.post(url, {"tag": tag},function() {
        obj.val("");
        if (nopopup === null) {
            show_popup(info);
        }
    });
}

function complete_tags(inputfield, callback) {
    var value = inputfield.val();
    $(".popcomplete").remove();
    if (value === "") {
        return;
    }
    var pos = inputfield.offset();
    var container = $("<div/>").addClass("popcomplete");
    container.css({
        "top":pos.top + inputfield.outerHeight(),
        "left": pos.left,
        "position": "absolute"
    });
    $("body").append(container);
    container.click(function () {container.remove();});
    $.get("/movies/tags/startswith/?text=" + value, function(data) {
        var ul = $("<ul/>");
        container.append(ul);
        $.each(data.tags, function(i, v) {
            var li = $("<li/>");
            li.text(v);
            ul.append(li);
            li.click(function () {
                inputfield.val(v);
                if (callback !== null) {
                    callback(inputfield);
                }
            });
        });
    });
}

function show_popup(movieurl) {
    $.get(movieurl, function (data) {
        $(".infodata").hide();
        var thumbs = template.thumbs(data);
        var tags = template.tags(data);
        var video = template.video(data);
        
        var t = $("#movie-"+data.id);
        var info = t.find(".infodata");
        info.find(".thumbsholder").html(thumbs);
        info.find(".tagsholder").html(tags);
        info.find(".videoholder").html(video);
        //run_hooks();
        $(".popcomplete").remove();
        info.show();
        //pop.click(function (e) {e.stopImmediatePropagation();});
        
        info.find(".close").click(function (event) {
            event.stopImmediatePropagation();
            info.hide();
            $(".popcomplete").remove();
        });
    });
}

function update_multiselect() {
    var selected = $(".mchecked");
    if (selected.length > 0) {
        $("#multitag").show();
    } else {
        $("#multitag").hide();
    }
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
        complete_tags(t, addtag);
    });    
    
    $("input#multitag-tag").keyup(function (event) {
        var t = $(this);
        complete_tags(t);
    });
    $("input.addtaginput").keydown(function (event) {
        var t = $(this);
        if ( event.which == 13 ) {
            addtag(t);
        }
    });
    
    $("input.multiselectbox").change(function () {
        var cb = $(this);
        var p = cb.parent().parent();
        if (this.checked) {
            p.addClass("mchecked");
        } else {
            p.removeClass("mchecked");
        }
        update_multiselect();
    });
    
    $("#select-none").click(function (e) {
        $(".movie").find(".multiselectbox").each(function () {
            this.checked = false;
            $(this).change();
        });
        e.preventDefault();
        return false;
    });
    
    $("#select-all").click(function (e) {
        $(".movie").find(".multiselectbox").each(function () {
            this.checked = true;
            $(this).change();
        });
        e.preventDefault();
        return false;
    });
    
    $("input#multitag-send").click(function (e) {
        var tag = $("#multitag-tag").val();
        var selected = $(".mchecked");
        var ids = [];
        selected.each(function () {
            ids.push($(this).data("id"));
        });
        var url = "/movies/movie/" + ids.join() +"/addtag/";
        $.post(url, {"tag": tag},function() {
            $("#multitag-tag").val("");
        });
        e.preventDefault();
        return false;
    });
    $("input.addtagbutton").click(function (e) {
        var t = $(this);
        var id = t.data("id");
        var t2 = $("#addtag-"+id);
        addtag(t2);
        e.preventDefault();
        return false;
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