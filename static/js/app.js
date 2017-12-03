$(document).on(
    "click",
    "a",
    function( event ){
        // Stop the default behavior of the browser, which
        // is to change the URL of the page.
        event.preventDefault();
        // Manually change the location of the page to stay in
        // "Standalone" mode and change the URL at the same time.
        location.href = $( event.target ).attr( "href" );
    }
);
$(function() {
});

function shutter_attr(device_row) {
    attributes = new Object();
    attributes['mode'] = device_row.find('.btn-group').find('button.active').attr('val');
    return attributes;
}


function boiler_attr(device_row) {
    attributes = new Object();
    attributes['mode'] = device_row.find('.btn-group').find('button.active').attr('val');
    return attributes;
}

function air_conditioner_attr(device_row, on_off_changed) {
    attributes = new Object();
    attributes['on_off-changed'] = on_off_changed;
    attributes['on_off'] = device_row.find('.deviceOn').prop('checked');
    attributes['fan'] = device_row.find(".btn-group[val='fan'] button.active").attr('val');
    attributes['temp'] = device_row.find('select :selected').val();
    attributes['mode'] = device_row.find(".btn-group[val='mode'] button.active").attr('val');
    return attributes;
}

function light_attr(device_row, on_off_changed) {
    attributes = new Object();
    attributes['device_on'] = !device_row.find('.deviceOn').prop('checked');
    return attributes;
}

function update_device(device_id, attributes) {
    $.ajax({
        type: "POST",
        url: 'update_device/' + device_id,
        data: attributes,
        success: success,
        error: function (XMLHttpRequest, textStatus, errorThrown) { displayErrorMessage(errorThrown); }
    });
};

//general turn scheduler on/off
function update_scheduler(is_on) {
    $.ajax({
        type: "POST",
        url: 'update_scheduler/' + is_on,
        success: success,
        error: function (XMLHttpRequest, textStatus, errorThrown) { displayErrorMessage(errorThrown); }
    });
};

function execute_scenario(scenario_name) {
    $.ajax({
        type: "POST",
        url: 'execute_scenario/' + scenario_name,
        success: success,
        error: function (XMLHttpRequest, textStatus, errorThrown) { displayErrorMessage(errorThrown); }
    });
};

function success(result) {
    res = JSON.parse(result);
    if (res.succeeded) {
        displayOkMessage();
    } else {
        displayErrorMessage(res.error);
    }
}

namespace = ''; // change to an empty string to use the global namespace
// the socket.io documentation recommends sending an explicit package upon connection
// this is specially important when using the global namespace
var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);


function update_device_websoc(device_id, attributes) {
    socket.emit('my broadcast event', {device_id: device_id, data: attributes}, callback = ack);
}

function ack(){
    displayOkMessage();
}

// websocket event handler for server sent data
socket.on('update_device', function(msg) {
    update_device_gui(msg.device,msg.status)
});

function displayErrorMessage(errorMessage) {
     $.notify("Error:"+ errorMessage, {position:"top left", autoHideDelay: 5000, showAnimation: 'fadeIn', hideAnimation: 'fadeOut'});
}

function displayOkMessage(errorMessage) {
     $.notify("Updated", {position:"top right", className: "success", autoHideDelay: 1000, showAnimation: 'fadeIn', hideAnimation: 'fadeOut'});
}