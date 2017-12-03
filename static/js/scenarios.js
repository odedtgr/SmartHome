$('button').on('click', function() {
    scenario_name = $(this).attr('val');
    execute_scenario(scenario_name);
});


// refresh every 1 hour to get latest devices status
setInterval(function() {
    location = '/';
}, 120000);