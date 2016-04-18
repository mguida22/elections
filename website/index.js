function random() {
  return Math.floor(Math.random() * 101);
}

var n = 50,
  duration = 750,
  now = new Date(Date.now() - duration);

var margin = {top: 20, right: 20, bottom: 20, left: 40},
    width = 400 - margin.left - margin.right,
    height = 200 - margin.top - margin.bottom;

var x = d3.time.scale()
    .domain([now - (n - 2) * duration, now - duration])
    .range([0, width]);

var y = d3.scale.linear()
    .domain([0, 100])
    .range([height, 0]);

var line = d3.svg.line()
    .interpolate("basis")
    .x(function(d, i) { return x(now - (n - 1 - i) * duration); })
    .y(function(d, i) { return y(d); });

function graph(id, types) {
  var svg = d3.select("#" + id + '-graph').append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  types.forEach(function(type) {
    var path = svg.append("g")
        .attr("clip-path", "url(#clip)")
      .append("path")
        .datum(data[id][type])
        .attr("class", "line-" + type);

    svg.append("defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", width)
        .attr("height", height);

    svg.append("g")
        .attr("class", "y axis")
        .call(d3.svg.axis().scale(y).orient("left"));

    var xAxis = svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(x.axis = d3.svg.axis().scale(x).orient("bottom"));

    var transition = d3.select({}).transition()
        .duration(750)
        .ease("linear");

    tick();
    function tick() {
      transition = transition.each(function() {
        // update the domains
        now = new Date();
        x.domain([now - (n - 2) * duration, now - duration]);

        // push new data point onto the back
        data[id][type].push(random());

        // redraw the line
        path.attr("d", line)
            .attr("transform", null);

        // slide the x-axis left
        xAxis.call(x.axis);

        // slide the line left
        path.transition()
            .attr("transform", "translate(" + x(now - (n - 1) * duration) + ")");

        // pop the old data point off the front
        data[id][type].shift();
      }).transition().each("start", tick);
    }
  });
}

data = {
  'clinton': {
    'pos': d3.range(n).map(random),
    'neg': d3.range(n).map(random),
  },
  'trump': {
    'pos': d3.range(n).map(random),
    'neg': d3.range(n).map(random),
  },
  'sanders': {
    'pos': d3.range(n).map(random),
    'neg': d3.range(n).map(random),
  },
  'cruz': {
    'pos': d3.range(n).map(random),
    'neg': d3.range(n).map(random),
  },
};

for (id in data) {
  graph(id, ['pos', 'neg']);
};
