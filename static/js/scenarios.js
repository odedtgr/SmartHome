$('button').on('click', function() {
    execute_scenario('Close living room');
});


// refresh every 1 hour to get latest devices status
setInterval(function() {
    location = '/';
}, 120000);