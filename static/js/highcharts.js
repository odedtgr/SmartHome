var dynamicChart;
var channelsLoaded = 0;
// put your ThingSpeak Channel#, Channel Name, and API keys here.
// fieldList shows which field you want to load, and which axis to display that field on, 
// the 'T' Temperature left axis, or the 'O' Other right axis.
var channelKeys =[];
//Change TO: display two fields from the same channel from a Rain gauge - 15min counts, and total counts
//  src="http://api.thingspeak.com/channels/8652/charts/3?width=1300&height=520&results=1000&dynamic=false&title=15minTotals%20(0.5mm)" ></iframe>
channelKeys.push({channelNumber:112955, name:'Temperature',key:'8UKAQRZZVL67BGVI',
    fieldList:[{field:3,axis:'C'}]});

// user's timezone offset
var myOffset = new Date().getTimezoneOffset();

// converts date format from JSON
function getChartDate(d) {
    // get the data using javascript's date object (year, month, day, hour, minute, second)
    // months in javascript start at 0, so remember to subtract 1 when specifying the month
    // offset in minutes is converted to milliseconds and subtracted so that chart's x-axis is correct
    return Date.UTC(d.substring(0,4), d.substring(5,7)-1, d.substring(8,10), d.substring(11,13), d.substring(14,16), d.substring(17,19)) - (myOffset * 60000);
}

//  This is where the chart is generated.
$(document).ready(function()
{
    var last_date; // variable for the last date added to the chart
    //make series numbers for each field
    var seriesCounter=0
    for (var channelIndex=0; channelIndex<channelKeys.length; channelIndex++)  // iterate through each channel
    {
        for (var fieldIndex=0; fieldIndex<channelKeys[channelIndex].fieldList.length; fieldIndex++)  // iterate through each channel
        {
            channelKeys[channelIndex].fieldList[fieldIndex].series = seriesCounter;
            seriesCounter++;
        }
    }
    //make calls to load data from each channel into channelKeys array now
    for (var channelIndex=0; channelIndex<channelKeys.length; channelIndex++)  // iterate through each channel
    {
        channelKeys[channelIndex].loaded = false;
        loadThingSpeakChannel(channelIndex,channelKeys[channelIndex].channelNumber,channelKeys[channelIndex].key,channelKeys[channelIndex].fieldList);

    }

    // load the most recent 8000 points (fast initial load) from a ThingSpeak channel into a data[] array and return the data[] array
    function loadThingSpeakChannel(sentChannelIndex,channelNumber,key,sentFieldList) {
        var fieldList= sentFieldList;
        var channelIndex = sentChannelIndex;
        // get the Channel data with a webservice call
        $.getJSON('https://www.thingspeak.com/channels/'+channelNumber+'/feed.json?callback=?&amp;offset=0&amp;results=8000;key='+key, function(data)
        {
            // if no access
            if (data == '-1') {
                $('#chart-container').append('This channel is not public.  To embed charts, the channel must be public or a read key must be specified.');
                window.console && console.log('Thingspeak Data Loading Error');
            }
            for (var fieldIndex=0; fieldIndex<fieldList.length; fieldIndex++)  // iterate through each field
            {
                fieldList[fieldIndex].data =[];
                for (var h=0; h<data.feeds.length; h++)  // iterate through each feed (data point)
                {
                    var p = []//new Highcharts.Point();
                    var fieldStr = "data.feeds["+h+"].field"+fieldList[fieldIndex].field;
                    var v = eval(fieldStr);
                    p[0] = getChartDate(data.feeds[h].created_at);
                    p[1] = parseFloat(v);
                    // if a numerical value exists add it
                    if (!isNaN(parseInt(v))) { fieldList[fieldIndex].data.push(p); }
                }
                fieldList[fieldIndex].name = eval("data.channel.field"+fieldList[fieldIndex].field);
            }
            channelKeys[channelIndex].fieldList=fieldList;
            channelKeys[channelIndex].loaded=true;
            channelsLoaded++;
            if (channelsLoaded==channelKeys.length){createChart();}
        })
            .fail(function() { alert('getJSON request failed! '); });
    }
    // create the chart when all data is loaded
    function createChart() {
        // specify the chart options
        var chartOptions = {
            chart:
            {
                renderTo: 'chart-container',
                zoomType:'y'
            },
            rangeSelector: {
                buttons: [{
                    count: 1,
                    type: 'hour',
                    text: '1H'
                }, {
                    count: 12,
                    type: 'hour',
                    text: '12H'
                }, {
                    count: 1,
                    type: 'day',
                    text: 'D'
                }, {
                    count: 1,
                    type: 'week',
                    text: 'W'
                }, {
                    count: 1,
                    type: 'month',
                    text: 'M'
                }, {
                    count: 1,
                    type: 'year',
                    text: 'Y'
                }, {
                    type: 'all',
                    text: 'All'
                }],
                inputEnabled: false,
                selected: 4  //Change to 4th button as default
            },
            title: {
                text: ''
            },
            plotOptions: {
                line: {
                    gapSize:5
                },
                series: {
                    connectNulls: true,
                    marker: {
                        radius: 2
                    },
                    animation: false,
                    step: false,
                    turboThrehold:1000,
                    borderWidth: 0
                }
            },
            tooltip: {
                valueDecimals: 1,
                valueSuffix: '',
                xDateFormat:'%Y-%m-%d<br/>%H:%M:%S %p'
            },
            xAxis: {
                type: 'datetime',
                ordinal:false,
                min: Date.UTC(2013,02,28),
                dateTimeLabelFormats : {
                    hour: '%l %p',
                    minute: '%l:%M %p'
                },
                title: {
                    text: 'LeftAxis'
                }
            },
            yAxis: [{
                title: {
                    text: ''
                },
                id: 'R'
            }, {
                title: {
                    text: 'Temperature'
                },
                opposite: true,
                id: 'C'
            }],
            legend: {
                enabled: false
            },
            navigator: {
                baseSeries: 0  //select which series to show in history navigator, First series is 0
            },
            series: []
        };
        // add all Channel data to the chart
        for (var channelIndex=0; channelIndex<channelKeys.length; channelIndex++)  // iterate through each channel
        {
            for (var fieldIndex=0; fieldIndex<channelKeys[channelIndex].fieldList.length; fieldIndex++)  // add each field
            {
                chartOptions.series.push({data:channelKeys[channelIndex].fieldList[fieldIndex].data,
                    index:channelKeys[channelIndex].fieldList[fieldIndex].series,
                    yAxis:channelKeys[channelIndex].fieldList[fieldIndex].axis,
                    //visible:false,
                    name: channelKeys[channelIndex].fieldList[fieldIndex].name});
            }
        }
        // set chart labels here so that decoding occurs properly
        //chartOptions.title.text = data.channel.name;
        chartOptions.xAxis.title.text = 'Date';
        // draw the chart
        dynamicChart = new Highcharts.StockChart(chartOptions);
    }
});