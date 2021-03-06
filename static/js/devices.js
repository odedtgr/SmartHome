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
    $(this).closest('.btn-group').find('button').removeClass('active');
    $(this).addClass('active');
    //scheduler general on-off button on devices window
    if ($(this).parent('.btn-group').attr('val') === 'scheduler')
        update_scheduler($(this).attr('val') === 'true');
    else
        device_changed($(this));
});

function device_changed(control) {
    if (control.parent('.btn-group').attr('ignore') === 'true')
        return;
    if (control.attr('ignore') === 'true')
        return;
    device_row = control.closest('.row');
    device_type = device_row.attr('device-type');
    device_name = device_row.attr('device-name');
    if (device_type === 'temperature')
        return;//add attribute for the collapse button .hasClass( "in" )
    else if (device_type === 'Shutter' || device_type === 'ShutterNew') {
        control.removeClass('btn-primary').addClass('btn-alert');
        attr = Shutter_attr(device_row);
    }
    else if(device_type === 'Boiler')
        attr = Boiler_attr(device_row);
    else if(device_type === 'AirConditioner')
        attr = AirConditioner_attr(device_row, control.find('.deviceOn').attr('val') === 'device_on');
    else if(device_type === 'Light') {
        attr = Light_attr(device_row);
        $(device_row).find('.btn-danger').removeClass("btn-danger").addClass("btn-default");
        $(device_row).find('.btn-primary').removeClass("btn-primary").addClass("btn-default");
    }
    update_device_websoc(device_name, attr);
}

//update device controls on the webapp
function update_device_gui(status, device_id, type){
    if(type == 'Boiler')
        update_Boiler_gui(device_id, status);
    else if(type == 'AirConditioner')
        update_AirConditioner_gui(device_id, status);
    else if(type == 'Shutter' || type == 'ShutterNew')
        update_Shutter_gui(device_id, status);
    else if(type == 'temperature')
        update_temperature_gui(device_id, status);
    else if(type == 'Light')
        update_Light_gui(device_id, status);
    else if(type == 'BoilerTemperature')
        update_bolier_temperature_gui(device_id, status);
}

function update_Boiler_gui(device_id, status){
    device = document.getElementById(device_id);
    $(device).find('.T').html(status.Temp);
    $(device).find('.btn-group').find('button').removeClass('active');
    if(status.mode == 0)
        $(device).find("[val=0]").addClass('active');
    else if(status.mode == 3 || status.mode == 4 || status.mode == 5 || status.mode == 6)
        $(device).find("[val=4]").addClass('active');
    else
        $(device).find("[val=2]").addClass('active');
}

function update_AirConditioner_gui(device_id, status){
    device = document.getElementById(device_id);
    if(status.device_on == 'true' || status.device_on == 'True')
        $(device).find('.deviceOn').prop('checked', true).change()
    else
        $(device).find('.deviceOn').prop('checked', false).change()
}

function update_Shutter_gui(device_id, status){
    device = document.getElementById(device_id);
    $(device).find('.btn-group').find('button').removeClass('active');
    $(device).find('.btn-group').find('button').removeClass('btn-alert').addClass('btn-primary')
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
function update_bolier_temperature_gui(device_id, status){
    device = document.getElementById(device_id);
    $(device).find('.T').html(" "+status.Temp);
}

function update_Light_gui(device_id, status) {
    device = document.getElementById(device_id);
    if (status.device_on == 'true' || status.on_off == 'True') {
        $(device).find('.deviceOn').prop('checked', true).change()
        $(device).find('.btn').removeClass("btn-default").addClass("btn-danger")
    }else {
        $(device).find('.deviceOn').prop('checked', false).change()
        $(device).find('.btn').removeClass("btn-default").addClass("btn-primary")
    }
}

// refresh every 1 hour to get latest devices status
setInterval(function() {
    location = '/';
}, 120000);