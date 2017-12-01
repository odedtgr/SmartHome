$('button').on('click', function() {
    execute_scenario('test_name');
});


// refresh every 1 hour to get latest devices status
setInterval(function() {
    location = '/';
}, 120000);