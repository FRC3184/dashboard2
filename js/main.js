var name_map = {};
var buffer_size = 200;
var my_grid = [100, 100];

var drag_opts = {
    grid: my_grid,
    stop: function(evt, ui) {
        ui.position = roundVector(ui.position, my_grid);
    }
};

function fitToContainer(canvas){
  // Make it visually fill the positioned parent
  canvas.style.width ='100%';
  canvas.style.height='100%';
  // ...then set the internal size to match
  canvas.width  = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
}

var resize_opts = {grid: my_grid, resize: function(event, ui) {
  fitToContainer(ui.element.children("canvas").get(0));
}};

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

var make_chart = function(data) {
  console.log(data.name);
  var chart_element = $("<canvas width=\"400px\" height=\"400px\" class=\"chart\"></canvas>");
  chart_element.appendTo("#dashboard");
  chart_wrapper = $("<div class=\"element-wrap ui-widget-content\" data-name=\"" + data.name + "\"></div>");
  chart_element.wrap(chart_wrapper);

  var my_chart = new Chart(chart_element, data.name);

  name_map[data.name] = my_chart;
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
    name_map[name].add_point({x: t, y: y});
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

$(document).ready(function() {

    $("#save-button").click(function() {
        $(".element-wrap").each(function(i, element) {
            element = $(element);  //Why jQuery doesn't return these as jQuery objects is beyond me.
            var name = element.data("name");
            var data = element.position();
            data.width = element.width();
            data.height = element.height();
            localStorage.setItem(name, JSON.stringify(data));
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
            var stored_data = localStorage.getItem(name);
            if (stored_data !== null) {
                stored_data = JSON.parse(stored_data);
                element.css(stored_data);
            }
            if (element.children("canvas").length > 0) {
                fitToContainer(element.children("canvas").get(0));
            }
        });
        console.log("Loaded positions");
    }, 500)
});
