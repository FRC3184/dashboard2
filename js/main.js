var name_map = {};
var buffer_size = 200;
var my_grid = [100, 100];
Chart.defaults.global.maintainAspectRatio = false;

var drag_opts = {
    grid: my_grid,
    stop: function(evt, ui) {
        ui.position = roundVector(ui.position, my_grid);
    }
};
var resize_opts = {grid: my_grid};

/*
 * Rounds both parts of vec_k to nearest roundMagnitude_k
 * Returns rounded vector
*/
function roundVector(vec, round) {
    var ret = vec;
    ret.left = Math.round(vec.left / round[0]) * round[0];
    ret.top = Math.round(vec.top / round[1]) * round[1];
    return ret;
}

var update_chart = function(data_t, data_y) {
  this.data.datasets[0].data.push({x: data_t, y: data_y});
  if (this.data.datasets[0].data.length > buffer_size) {
    this.data.datasets[0].data = this.data.datasets[0].data.slice(1);
  }
  this.update();
};

var make_chart = function(data) {
  console.log(data.name);
  var chart_element = $("<canvas width=\"400px\" height=\"400px\" class=\"chart\"></canvas>");
  chart_element.appendTo("#dashboard");
  chart_wrapper = $("<div class=\"element-wrap ui-widget-content\" data-name=\"" + data.name + "\"></div>");
  chart_element.wrap(chart_wrapper);

  var chart = new Chart(chart_element, {
    type: "line",
    data: {
      datasets: [{
        label: data.name,
        data: []
      }]
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        xAxes: [{
          type: 'linear',
          position: 'bottom'
        }]
      }
    }
  });

  name_map[data.name] = chart;
  chart.update_data = update_chart;

};

var source = new EventSource("/events");
source.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    alert("The server says " + data.message);
}, false);
source.addEventListener('data', function(event) {
  var data = JSON.parse(event.data);
  var name = data.name;
  var t = data.time;
  var y = data.value;

  if (name in name_map) {
    name_map[name].update_data(t, y);
  }
});
source.addEventListener("action", function(event) {
  var data = JSON.parse(event.data);
  console.log(data);
  switch (data.action) {
    default:
      if (data.name in name_map) {
        break;
      }
    case "make_chart":
      make_chart(data);
      break;
  }
});

function stringifyPosition(position) {
    return position.top + "," + position.left;
}
function destringifyPosition(str) {
    var obj = {};
    var split = str.split(",");
    obj.top = parseInt(split[0]);
    obj.left = parseInt(split[1]);
    return obj;
}

$(document).ready(function() {

    $("#save-button").click(function() {
        $(".element-wrap").each(function(i, element) {
            element = $(element);  //Why jQuery doesn't return these as jQuery objects is beyond me.
            var name = element.data("name");
            localStorage.setItem(name + ".position", stringifyPosition(element.position()));
            localStorage.setItem(name + ".size", element.width() + "," + element.height());
        });
    });
    $("#refresh-button").click(function() {
        source.close();
        location.reload();
    });

    setTimeout(function() {
        $(".element-wrap").draggable(drag_opts).resizable(resize_opts).draggable("disable");

        $("#editable-check").change(function() {
            $(".element-wrap").draggable(this.checked ? "enable" : "disable");
            $(".element-wrap").resizable(this.checked ? "enable" : "disable");
        });

        console.log("Loading positions...");
        $(".element-wrap").each(function(i, element) {
            element = $(element);  //Why jQuery doesn't return these as jQuery objects is beyond me.
            var name = element.data("name");
            var position = localStorage.getItem(name + ".position");
            var size = localStorage.getItem(name + ".size");
            if (position !== null) {
                var newPos = destringifyPosition(position);
                element.css({top: newPos.top, left: newPos.left});
            }
            if (size !== null) {
                var newSize = destringifyPosition(size);
                element.css({width: newSize.top, height: newSize.left});
            }
        });
        console.log("Loaded positions");
    }, 500)
});
