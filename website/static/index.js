var d;
var source = new EventSource('events/');
source.onmessage = function(e) {
  d = JSON.parse(e.data);
  if (d) {
    groups.sanders.pos.val = d.berniesanders.Positive * 100;
    groups.sanders.neg.val = d.berniesanders.Negative * 100;
    groups.trump.pos.val = d.donaldtrump.Positive * 100;
    groups.trump.neg.val = d.donaldtrump.Negative * 100;
    groups.clinton.pos.val = d.hillaryclinton.Positive * 100;
    groups.clinton.neg.val = d.hillaryclinton.Negative * 100;
    groups.cruz.pos.val = d.tedcruz.Positive * 100;
    groups.cruz.neg.val = d.tedcruz.Negative * 100;
  }
};

var n = 50,
  duration = 2000,
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

function graph(id) {
  var svg = d3.select("#" + id + '-graph').append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  groups[id].xAxis = svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(x.axis = d3.svg.axis().scale(x).orient("bottom"));

  groups[id].paths = svg.append('g');

  var yAxis = svg.append("g")
      .attr("class", "y axis")
      .call(d3.svg.axis().scale(y).orient("left"));

  ['pos', 'neg'].forEach(function(type) {
    groups[id][type].path = groups[id].paths
      .append('path')
      .data([groups[id][type].data])
      .attr("class", "line-" + type);

    // groups[id][type].path = svg.append('g')
    //   .attr("clip-path", "url(#clip)")
    //   .append('path')
    //   .data([groups[id][type].data])
    //   .attr("class", "line-" + type);

    // svg.append("defs").append("clipPath")
    //   .attr("id", "clip")
    // .append("rect")
    //   .attr("width", width)
    //   .attr("height", height);
  });
}

function tick() {
  now = new Date();

  for (id in groups) {
    ['pos', 'neg'].forEach(function(type) {
      groups[id][type].data.push(groups[id][type].val);
      // groups[id][type].data.push(20 + Math.random() * 100);
      groups[id][type].path.attr('d', line);
    });
  }

  x.domain([now - (n - 2) * duration, now - duration]);

  for (id in groups) {
    groups[id].xAxis.transition()
      .duration(duration)
      .ease('linear')
      .call(x.axis);

    groups[id].paths.attr('transform', null)
      .transition()
      .duration(duration)
      .ease('linear')
      .attr('transform', 'translate(' + x(now - (n - 1) * duration) + ')')
      .each('end', tick);

    ['pos', 'neg'].forEach(function(type) {
      groups[id][type].data.shift();
    });
  }
}

var groups = {
  clinton: {
    pos: {
      data: d3.range(n).map(function() { return 0; }),
      val: 0,
    },
    neg: {
      data: d3.range(n).map(function() { return 0; }),
      val: 0,
    }
  },
  trump: {
    pos: {
      data: d3.range(n).map(function() { return 0; }),
      val: 0,
    },
    neg: {
      data: d3.range(n).map(function() { return 0; }),
      val: 0,
    }
  },
  sanders: {
    pos: {
      data: d3.range(n).map(function() { return 0; }),
      val: 0,
    },
    neg: {
      data: d3.range(n).map(function() { return 0; }),
      val: 0,
    }
  },
  cruz: {
    pos: {
      data: d3.range(n).map(function() { return 0; }),
      val: 0,
    },
    neg: {
      data: d3.range(n).map(function() { return 0; }),
      val: 0,
    }
  },
};

for (id in groups) {
  graph(id);
};

tick();
