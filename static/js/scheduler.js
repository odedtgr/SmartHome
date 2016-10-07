var new_schedule_item_index = 999;
function bindPanelControls(panel) {
    if (panel === undefined) {
        panel = $('.schedule_item');
    }
    panel.find('.clockpicker').clockpicker();
    panel.find('select.device').off('change').on('change', onSelectDeviceChange);
    panel.find('button.remove').off('click').on('click', onRemoveButtonClick);
    panel.find('select.device').trigger('change');
}

function onSelectDeviceChange() {
    var schedule_index = $(this).attr('schedule_index');
    $.ajax({
        type: "POST",
        url: "device_config_panel/" + $(this).val() + "/" + schedule_index,
        error: function (XMLHttpRequest, textStatus, errorThrown) { displayErrorMessage(errorThrown); },
        success: function(panel) {
            $(".device_config[schedule_index='" + schedule_index + "']").html(panel);
            $('.btn-group button').off('click').on('click', onButtonGroupClick);
            $('input[type=checkbox][data-toggle^=toggle]').bootstrapToggle()
        }
  });
}

function onRemoveButtonClick() {
    $(this).parents('.schedule_item').remove();
}

function onButtonGroupClick() {
    $(this).parents('.btn-group').find('button').removeClass('active')
    $(this).addClass('active');
}

bindPanelControls();

$('button.add').on('click', function() {
    $.ajax({
      type: "POST",
      url: "new_schedule_item_panel/" + new_schedule_item_index,
      error: function (XMLHttpRequest, textStatus, errorThrown) { displayErrorMessage(errorThrown); },
      success: function(panel) {
            $('#buttons_panel').before(panel);
            bindPanelControls($('.schedule_item').last());
        }
  });
    new_schedule_item_index--;
});

$('button.save').on('click', function() {
    var scheduler = [];
    $('.schedule_item').each(function(index) {
        var curr_item = {
            'enabled':   $(this).find(".task_enabled").attr('value') === 'true',
            'device_id': parseInt($(this).find('select.device').val()),
            'hour':      $(this).find('.time-select').val(),
            'day':       [],
            'config':    {}
        };

        // insert days
        $(this).find('input:checkbox:checked').each(function() { curr_item['day'].push($(this).val()) });

        // insert config
        device_row = $(this).find("div[device-type]");
        device_type = device_row.attr('device-type');
        if (device_type === 'shutter' || device_type === 'shutterNew')
            attr = shutter_attr(device_row);
        else if(device_type === 'boiler')
            attr = boiler_attr(device_row);
        else if(device_type === 'air_conditioner')
            attr = air_conditioner_attr(device_row, false);
        curr_item['config'] = attr;

        scheduler.push(curr_item);
    });

    $.ajax({
      type: "POST",
      url: "update_scheduler",
      data: { scheduler: JSON.stringify(scheduler) },
      success: success,
      error: function (XMLHttpRequest, textStatus, errorThrown) { displayErrorMessage(errorThrown); }
  });
});

