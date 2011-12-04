$(document).ready(function() {

    var update_img2011 = function() {
        event.preventDefault();
        $("#img2011").css("display", "block");
    };
    
    $("#ver2010").click(function () {
        update_img2011();
    });

        
    });