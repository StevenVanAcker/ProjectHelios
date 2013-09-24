function renderGUI(data) {
    //console.log(data);
    guiUpdateArrows("left", data.statLeft);
    guiUpdateArrows("right", data.statRight);
    guiUpdateArrows("vert", data.statVert);
    updateDistanceHistory(data.altitudeHistory);

    toggleSwitchTo("#setAuto", data.maintainAltitude);
    toggleSwitchTo("#setSingleSteering", data.singleSteeringMode);
    toggleSwitchTo("#setForceDescent", data.forceDescent);

}

function guiUpdateArrows(name, state) {
    switch(state) {
	case "forward":
	    //console.log("Motor "+name+" = forward");
	    $("#" + name + "-forward").addClass("bigbutton-active").removeClass("bigbutton-inactive");
	    $("#" + name + "-backward").addClass("bigbutton-inactive").removeClass("bigbutton-active");
	    break;
	case "backward":
	    //console.log("Motor "+name+" = backward");
	    $("#" + name + "-forward").addClass("bigbutton-inactive").removeClass("bigbutton-active");
	    $("#" + name + "-backward").addClass("bigbutton-active").removeClass("bigbutton-inactive");
	    break;
	default:
	    //console.log("Motor "+name+" = stop");
	    $("#" + name + "-forward").addClass("bigbutton-inactive").removeClass("bigbutton-active");
	    $("#" + name + "-backward").addClass("bigbutton-inactive").removeClass("bigbutton-active");
	    break;
    }
}

var lastDistanceHistoryTimestamp = -1;

var graphAddPoint = function(p) { }; // is set later on as a closure
var graphRedraw = function() { }; // is set later on as a closure
function updateDistanceHistory(newdata) {
    for(var i = 0; i < newdata.length; i++) {
        var p = newdata[i];
	var ts = p[0];
	var val = p[1];

	if(ts > lastDistanceHistoryTimestamp) {
	    graphAddPoint(p);
	    lastDistanceHistoryTimestamp = ts;
	}
	graphRedraw();
    }
}


function goLeft() { $.getJSON("/call/turnLeft", renderGUI); }
function goRight() { $.getJSON("/call/turnRight", renderGUI); }
function goForward() { $.getJSON("/call/forward", renderGUI); }
function goBackward() { $.getJSON("/call/backward", renderGUI); }
function goUp() { $.getJSON("/call/up", renderGUI); }
function goDown() { $.getJSON("/call/down", renderGUI); }
function updateGUI() { $.getJSON("/call/status", renderGUI); }
function setAuto(val) { $.getJSON("/call/setAuto/"+val, renderGUI); }
function setSingleSteerMode(val) { $.getJSON("/call/setSingleSteerMode/"+val, renderGUI); }
function setForceDescent(val) { $.getJSON("/call/setForceDescent/"+val, renderGUI); }

$(function() {
	$( "#left-forward" ).click(goRight);
	$( "#right-forward" ).click(goLeft);
	$( "#left-backward" ).click(goLeft);
	$( "#right-backward" ).click(goRight);
	$( "#vert-forward" ).click(goUp);
	$( "#vert-backward" ).click(goDown);
});

// Keypress handling {{{
$(document).keydown(function(e) {

  switch(e.keyCode) {
      case 37: /* left key */
	goLeft();
	break;
      case 38: /* up key */
	goForward();
	break;
      case 39: /* right key */
	goRight();
	break;
      case 40: /* down key */
	goBackward();
	break;
      case 32: /* space */
	goUp();
	break;
      case 68: /* 'd' */
	goDown();
	break;
      default:
	console.log("Unknown key pressed: "+e.keyCode);
	break;
  }
});
// }}}
// Altitude graphing {{{
$(function () {
    $(document).ready(function() {
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
    
        var chart;
	$('#altitudeGraph').highcharts({
            chart: {
                type: 'spline',
                animation: Highcharts.svg, // don't animate in old IE
                marginRight: 10,
                events: {
                    load: function() {
                        var series = this.series[0];
			graphAddPoint = function(p) {
                            series.addPoint(p, false, true);
			}
			graphRedraw = function() { $('#altitudeGraph').highcharts().redraw(); }
                    }
                }
            },
            title: {
                text: 'Airship altitude (cm)'
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150
            },
            yAxis: {
                title: {
                    text: 'Altitude (cm)'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                formatter: function() {
                        return '<b>'+ this.series.name +'</b><br/>'+
                        Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) +'<br/>'+
                        Highcharts.numberFormat(this.y, 2);
                }
            },
            legend: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            series: [{
                name: 'Airship altitude (cm)',
                data: (function() {
                    var data = [], time = (new Date()).getTime(), i;
    
                    for (i = -20; i <= 0; i++) {
                        data.push({
                            x: time + i * 100,
                            y: null
                        });
                    }
                    return data;
                })()
            }]
        });
    });
    
});
// }}}
// toggle switches {{{
var toggleFunctions = {};

function initToggleSwitch(id, callback) {
    $(function() { $(id).toggleSwitch({
	exportGuts: function (e) {
	    toggleFunctions[id] = e;
	},
    	change: function(e) {
	    callback(id, e[1].value == 0);
	} 
    });});
}

function toggleSwitchTo(id, val) {
    if(id in toggleFunctions) {
	//console.log("Setting "+id+" to "+val);
        toggleFunctions[id](val ? 0 : 1);
    }
}
// }}}

initToggleSwitch("#setAuto", function(i, v) {
    setAuto(v);
});

initToggleSwitch("#setSingleSteering", function(i, v) {
    setSingleSteerMode(v);
});

initToggleSwitch("#setForceDescent", function(i, v) {
    setForceDescent(v);
});

setInterval(updateGUI, 200);
