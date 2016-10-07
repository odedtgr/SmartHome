$('select').on('change', function(event, state) {
    device_changed($(this));
});

$('.form-control').on('change', function(event, state) {
    device_changed($(this));
});
$('.toggle_div').on('click', function(event, state) {
    device_changed($(this));
});

$('button').on('click', function() {
    $(this).closest('.btn-group').find('button').removeClass('active')
    $(this).addClass('active');
    //scheduler general on-off button on devices window
    if ($(this).parent('.btn-group').attr('val') === 'scheduler')
        update_scheduler($(this).attr('val') === 'true');
    else
        device_changed($(this));
});

function device_changed(control) {
    device_row = control.closest('.row');
    device_type = device_row.attr('device-type');
    device_id = device_row.attr('id');
    if (device_type === 'temperature')
        return;
    else if (device_type === 'shutter' || device_type === 'shutterNew')
        attr = shutter_attr(device_row);
    else if(device_type === 'boiler')
        attr = boiler_attr(device_row);
    else if(device_type === 'air_conditioner')
        attr = air_conditioner_attr(device_row, control.find('.deviceOn').attr('val') === 'on_off');
    update_device(device_id, attr);
}

//update device controls on the webapp
function update_device_gui(device, status){
    if(device.type == 'boiler')
        update_boiler_gui(device.id, status);
    else if(device.type == 'air_conditioner')
        update_air_conditioner_gui(device.id, status);
    else if(device.type == 'shutter' || device.type == 'shutterNew')
        update_shutter_gui(device.id, status);
    else if(device.type == 'temperature')
        update_temperature_gui(device.id, status);
}

function update_boiler_gui(device_id, status){
    device = document.getElementById(device_id);
    $(device).find('.btn-group').find('button').removeClass('active');
    if(status.mode == 0 || status.mode == 4)
        $(device).find("[val=4]").addClass('active');
    else if(status.mode == 1)
        $(device).find("[val=1]").addClass('active');
    else
        $(device).find("[val=3]").addClass('active');
}

function update_air_conditioner_gui(device_id, status){
    device = document.getElementById(device_id);
    if(status.on_off == 'true' || status.on_off == 'True')
        $(device).find('.deviceOn').prop('checked', true).change()
    else
        $(device).find('.deviceOn').prop('checked', false).change()
}

function update_shutter_gui(device_id, status){
    device = document.getElementById(device_id);
    $(device).find('.btn-group').find('button').removeClass('active');
    if(status.mode == 0 || status.mode == 25 || status.mode == 50 || status.mode == 75 || status.mode == 100) {
        $(device).find('.status').html("");
        $(device).find("[val=" + status.mode + "]").addClass('active');
    }
    else {
        $(device).find('.status').html(status.mode + "% Open");
        //$(device).find('.progress-bar').css('width', status.mode+'%');
        //$(device).find('.progress-bar').html(status.mode+'%');
    }
}

function update_temperature_gui(device_id, status){
    device = document.getElementById(device_id);
    $(device).find('.T').html("T= "+status.Temp+" C");
    $(device).find('.RH').html("RH= "+status.Rh);
}

// refresh every 1 hour to get latest devices status
setInterval(function() {
    location = '/';
}, 120000);