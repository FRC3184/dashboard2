var name_map = {};
var buffer_size = 200;
var my_grid = [200, 200];
Chart.defaults.global.maintainAspectRatio = false;

var update_chart = function(data_t, data_y) {
  this.data.datasets[0].data.push({x: data_t, y: data_y});
  if (this.data.datasets[0].data.length > buffer_size) {
    this.data.datasets[0].data = this.data.datasets[0].data.slice(1);
  }
  this.update();
};

var make_chart = function(data) {
  console.log(data.name);
  var chart_element = $("<canvas data-name=\"" + data.name + "\" width=\"400px\" height=\"400px\" class=\"chart\"></canvas>");
  chart_element.appendTo("#dashboard");
  chart_wrapper = $("<div class=\"chart-wrap ui-widget-content\"></div>");
  chart_element.wrap(chart_wrapper);

  $(".chart-wrap").draggable({grid: my_grid}).resizable({grid: my_grid});
  console.log(chart_element);
  console.log(chart_wrapper);
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