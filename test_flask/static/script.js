'use strict';

window.addEventListener('load', function () {

    console.log("Hello World!");
    $("#output").text("hi");
});


function sendData() {
    var value = "hi";
    console.log(value);
    $.ajax({
        url: '/process',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'value': value }),
        success: function(response) {
            $("#output").text(response.result);
        },
        error: function(error) {
            console.log(error);
        }
    });
}