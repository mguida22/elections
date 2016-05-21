// create a new EventSource for server side events
var d;
var source = new EventSource('events/');
source.onmessage = function(e) {
  // parse incoming data from the server
  // if data is valid then update our group values for the graphs to pull from
  // set the data on the 'val' field instead of the 'data' field so that
  // we can accomodate for irregularities in when we recieve data. If too
  // many points come in we throw out older values, if they are at odd intervals
  // we don't need to handle updating irregularly
  d = JSON.parse(e.data);
  if (d) {
    groups.sanders.pos.val = d.berniesanders.Positive;
    groups.sanders.neg.val = d.berniesanders.Negative;
    groups.trump.pos.val = d.donaldtrump.Positive;
    groups.trump.neg.val = d.donaldtrump.Negative;
    groups.clinton.pos.val = d.hillaryclinton.Positive;
    groups.clinton.neg.val = d.hillaryclinton.Negative;
  }
};

// how many datapoints to display on a graph
var n = 50;
// how long between updating the graph
var duration = 500;
// get the current time - duration
var now = new Date(Date.now() - duration);

// set margins, width, height of the graphs
var margin = {
    top: 20,
    right: 20,
    bottom: 20,
    left: 40
  },
  width = 400 - margin.left - margin.right,
  height = 200 - margin.top - margin.bottom;

// x scaling
// time scale, moving along with the data
var x = d3.time.scale()
  .domain([now - (n - 2) * duration, now - duration])
  .range([0, width]);

// y scaling
// linear scale to follow data (0-100%)
var y = d3.scale.linear()
  .domain([-80, 80])
  .range([height, 0]);

// line computation
// interpolate between points to smooth data
// slide data with time, leave datapoint fixed in y direction
var line = d3.svg.line()
  .interpolate("basis")
  .x(function(d, i) {
    return x(now - (n - 1 - i) * duration);
  })
  .y(function(d, i) {
    return y(d);
  });

// generate initial graphs for each given id
function graph(id) {
  // grab the proper id and add an svg to it
  // set the width and height of our graph
  // center it in the div
  var svg = d3.select("#" + id + '-graph').append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // x axis for each group
  groups[id].xAxis = svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(x.axis = d3.svg.axis().scale(x).orient("bottom"));

  // holder for each path per graph
  groups[id].paths = svg.append('g');

  // y axis for the graph
  var yAxis = svg.append("g")
    .attr("class", "y axis")
    .call(d3.svg.axis().scale(y).orient("left"));

  // for both positive and negative sentiment data
  // tell the path to get it's data from the proper group id
  // ex: groups['sanders']['pos']
  // add a path with the propper class (for styling)
  ['pos', 'neg'].forEach(function(type) {
    groups[id][type].path = groups[id].paths
      .append('path')
      .data([groups[id][type].data])
      .attr("class", "line-" + type);
  });
}

// tick function to advance each line in each graph
function tick() {
  // get the current time
  now = new Date();

  // for the pos/neg lines for every candidate that we have
  for (id in groups) {
    ['pos', 'neg'].forEach(function(type) {
      // pull in the staged value to the graph
      groups[id][type].data.push(groups[id][type].val);
      // generate random data - handy for testing without a data source
      // groups[id][type].data.push(20 + Math.random() * 100);
      // compute the new path now that we have a new datapoint
      groups[id][type].path.attr('d', line);
    });
  }

  // move the x domain allong with time
  x.domain([now - (n - 2) * duration, now - duration]);

  // for every candidate
  for (id in groups) {
    // update the x-axis with our new domain
    // use a transition to smooth the appearance
    groups[id].xAxis.transition()
      .duration(duration)
      .ease('linear')
      .call(x.axis);

    if (id === 'clinton') {
      // smoothly transition each path with time
      // at the end of the first candidate's transition, call 'tick' again
      groups[id].paths.attr('transform', null)
        .transition()
        .duration(duration)
        .ease('linear')
        .attr('transform', 'translate(' + x(now - (n - 2) * duration) + ')')
        .each('end', tick);
    } else {
      // smoothly transition each path with time
      // don't call tick here, as we called it at the end of the first candidate
      groups[id].paths.attr('transform', null)
        .transition()
        .duration(duration)
        .ease('linear')
        .attr('transform', 'translate(' + x(now - (n - 2) * duration) + ')')
    }

    // for each candidate's pos/neg data, move the oldest point off of the graph
    ['pos', 'neg'].forEach(function(type) {
      groups[id][type].data.shift();
    });
  }
}

// maintain a structure of all of our groups for the graph
// each candidate has the following structure
//
// candidateName: {
//   sentimentType: {
//     data:
//       an array to hold all of the values in the graph
//       as data is pushed into the array or shifted off,
//       it will move in/out of the graph.
//       for the initial 'n' values, fill data with an array of zeros
//       so that our graph starts off with data in it
//     val:
//       the next value to put into the graph
//       storing seperately allows for irregularities in the source of data
//       and we can update on our own interval
//   },
//   ...
// }
var groups = {
  clinton: {
    pos: {
      data: d3.range(n).map(function() {
        return 0;
      }),
      val: 0,
    },
    neg: {
      data: d3.range(n).map(function() {
        return 0;
      }),
      val: 0,
    }
  },
  trump: {
    pos: {
      data: d3.range(n).map(function() {
        return 0;
      }),
      val: 0,
    },
    neg: {
      data: d3.range(n).map(function() {
        return 0;
      }),
      val: 0,
    }
  },
  sanders: {
    pos: {
      data: d3.range(n).map(function() {
        return 0;
      }),
      val: 0,
    },
    neg: {
      data: d3.range(n).map(function() {
        return 0;
      }),
      val: 0,
    }
  },
};

// initialize a graph for each candidate
for (id in groups) {
  graph(id);
};

// start advancing 'time'
tick();
