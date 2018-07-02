charts = {};

window.onload = function () {
  initCharts();
}

function initCharts() {
  let chartDetails = {
    traWhole: {
      labels: ['Points', 'Frame', 'Key-Value']
    },
    framegroup: {
      labels: ['Points', 'Frame']
    },
    changepoints: {
      labels: ['Points', 'Points sorted', 'Frame']
    },
    profit: {
      labels: ['Points', 'Points sorted', 'ST precalculated', ['Points', 'manual distance']]
    },
    profitAll: {
      labels: ['Points sorted', 'ST precalculated', ['Points', 'manual distance']]
    }
  };
  for (chartName in chartDetails) {
    let ctx = document.getElementById('chart-' + chartName);
    charts[chartName] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: chartDetails[chartName].labels,
        datasets: [{
          label: 'SQL time ms',
          backgroundColor: '#0000ff',
          data: [],
          borderWidth: 1
        },{
          label: 'Python time ms',
          backgroundColor: '#ff0000',
          data: [],
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            },
            stacked: true
          }],
          xAxes: [{
            stacked: true
          }],
        },
        tooltips: {
          mode: 'index',
          intersect: false,
        }
      }
    });
  }
}

function clearDataSets(chart) {
  for (dataset of charts[chart].data.datasets) {
    dataset.data = [];
  }
}

function showChart(chartName, data) {
  clearDataSets(chartName);
  charts[chartName].data.datasets[0].data = data.sql;
  charts[chartName].data.datasets[1].data = data.python;
  charts[chartName].update();
}

async function loadData(urls) {
  let results = {
    sql: [],
    python: []
  };
  for (let i in urls) {
    await $.getJSON(urls[i])
      .then((data) => {
        results.sql[i] = data.performance.sql;
        results.python[i] = data.performance.python;
      });
  }
  return results;
}

async function showTraWhole() {
  let trajectoryId = parseInt($('#input-traWhole').val());
  let data = await loadTraWhole(trajectoryId);
  showChart('traWhole', data);
}

function loadTraWhole(trajectoryId) {
  return loadData(['/trajectory_point/' + trajectoryId,
  '/trajectory_frame/' + trajectoryId,
  '/trajectory_keyvalue/' + trajectoryId]);
}

async function showFramegroup() {
  let framegroup = parseInt($('#input-framegroup').val());
  let granularity = parseInt($('#input-granularity').val());
  
  let data = await loadFramegroup(framegroup, granularity);
  showChart('framegroup', data);
}

function loadFramegroup(framegroup, granularity) {
  return loadData(['/timeframe_granularity_points/' + framegroup + '/' + granularity,
                  '/timeframe_granularity/' + framegroup + '/0/' + granularity]);
}

async function showChangepoints() {
  let framegroup = parseInt($('#input-changepoints-framegroup').val());
  let granularity = parseInt($('#input-changepoints-granularity').val());
  let mode = $('[name="input-changepoints-mode"]:checked').val();
  
  let data = await loadChangepoints(framegroup, granularity, mode);
  showChart('changepoints', data);
}

function loadChangepoints(framegroup, granularity, mode) {
  return loadData(['/changepoints_points/' + mode + '/' + framegroup + '/' + granularity,
                  '/changepoints_points_sorted/' + mode + '/' + framegroup + '/' + granularity,
                  '/changepoints/' + mode + '/' + framegroup + '/' + granularity]);
}

async function showProfit() {
  let trajectoryId = parseInt($('#input-profit').val());
  
  let data = await loadProfit(trajectoryId);
  showChart('profit', data);
}

function loadProfit(trajectoryId) {
  return loadData(['/profit/' + trajectoryId,
                  '/profit_sorted/' + trajectoryId,
                  '/profit_precalculated_st/' + trajectoryId,
                  'profit_manual/' + trajectoryId]);
}

async function showProfitAll() {  
  let data = await loadProfitAll();
  showChart('profitAll', data);
}

async function loadProfitAll(trajectoryId) {
  let data = {
    sql: [575031.241, 101102.274],
    python: [0, 0]
  };
  let liveData = await loadData(['/profit_manual']);
  console.log(liveData);
  data.sql = data.sql.concat(liveData.sql);
  data.python = data.python.concat(liveData.python);
  return data;
}
