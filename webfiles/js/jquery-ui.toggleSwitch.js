jQuery.fn.toggleSwitch = function (params) {

    var defaults = {
        highlight: true,
        width: 25,
        change: null,
        stop: null,
	exportGuts: null //this function will be given a callback function that allows setting the value of the toggleswitch
    };

    var options = $.extend({}, defaults, params);

    return $(this).each(function (i, item) {
        generateToggle(item);
    });

    function generateToggle(selectObj) {

        var silent = true;

        // create containing element
        var $contain = $("<div />").addClass("ui-toggle-switch");

        // generate labels
        $(selectObj).find("option").each(function (i, item) {
            $contain.append("<label>" + $(item).text() + "</label>");
        }).end().addClass("ui-toggle-switch");

        // generate slider with established options
        var $slider = $("<div />").slider({
            min: 0,
            max: 100,
            animate: "fast",
            change: function(e) { 
		    if(!silent && options.change) {
			options.change(arguments);
		    //} else {
			//e.preventDefault();
		    }
		},
            stop: function (e, ui) {
                var roundedVal = Math.round(ui.value / 100);
                var self = this;
                window.setTimeout(function () {
                    toggleValue(self.parentNode, roundedVal);
                }, 11);

                if(typeof options.stop === 'function') {
                    options.stop.call(this, e, roundedVal);
                }
            },
            range: (options.highlight && !$(selectObj).data("hideHighlight")) ? "max" : null
        }).width(options.width);

        // put slider in the middle
        $slider.insertAfter(
            $contain.children().eq(0)
        );

        // bind interaction
        $contain.on("click", "label", function () {
            var labelIndex = ($(this).is(":first-child")) ? 0 : 1;
            if ($(this).hasClass("ui-state-active")) {
                labelIndex = 1 - labelIndex;
            }
            toggleValue(this.parentNode, labelIndex);
        });

        function toggleValue(slideContain, index) {
            var $slideContain = $(slideContain), $parent = $slideContain.parent();
            $slideContain.find("label").eq(index).addClass("ui-state-active").siblings("label").removeClass("ui-state-active");
            $parent.find("option").prop("selected", false).eq(index).prop("selected", true);
            $parent.find("select").trigger("change");
            $slideContain.find(".ui-slider").slider("value", index * 100);
        }

        // initialise selected option
        $contain.find("label").eq(selectObj.selectedIndex).click();

        // add to DOM
        $(selectObj).parent().append($contain);

	if(typeof options.exportGuts === 'function') {
	    options.exportGuts.call(this, function() {
	    	return function(x) {
		    var oldsilent = silent;
		    silent = true;
		    toggleValue($contain, x);
		    silent = oldsilent;
		};
	    }());
	}

	silent = false;
    }
};
