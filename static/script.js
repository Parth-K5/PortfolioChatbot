$(document).ready(function() {
    $("#messageArea").on("submit", function(event) {
        const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const time = hour+":"+minute;
        var userText = $("#text").val();

        var userHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + userText + '<span class="msg_time_send">'+ time + '</span></div><div class="img_cont_msg"><img src="https://i.ibb.co/d5b84Xw/Untitled-design.png" class="rounded-circle user_img_msg"></div></div>';
        
        $("#text").val("");
        $("#messageAreaJS").append(userHtml);

        $.ajax({
            data: {
                msg: userText,	
            },
            type: "POST",
            url: "/get",
        }).done(function(data) {
            var botHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="https://st2.depositphotos.com/1006536/11500/v/950/depositphotos_115007176-stock-illustration-colorful-minimal-cloud-computing-digital.jpg" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + data + '<span class="msg_time">' + time + '</span></div></div>';
            $("#messageAreaJS").append($.parseHTML(botHtml));
        });
        event.preventDefault();
    });
});

$(document).ready(function() {
    var max = 50;
    $('#characters-feedback').html(0 + '/50');

    $('#text').keyup(function() {
        var text_length = $('#text').val().length;
        var text_remaining = max - text_length;

        $('#characters-feedback').html(text_remaining + '/50');
    });
});