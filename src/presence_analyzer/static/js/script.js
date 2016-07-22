function parseInterval(value) {
            var result = new Date(1,1,1);
            result.setMilliseconds(value*1000);
            return result;
        }

google.load("visualization", "1", {packages:["corechart", "timeline"], 'language': 'pl'});

$(document).ready( function() {
    $('#user_id').change( function() {
        var selected_user = $("#user_id").val();
        $.getJSON("/api/v1/user/"+selected_user, function(result) {
            var userImage = $("#user_image");
            userImage.attr('src', result.avatar_url);
        });
    });
});
