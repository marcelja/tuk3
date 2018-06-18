charts = {};

window.onload = function () {
  initCharts();
}

function initCharts() {
  let chartNames = ['traWhole'];
  for (chartName of chartNames) {
    let ctx = document.getElementById('chart-' + chartName);
    charts[chartName] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ["Points", "Frame", "Key-Value"],
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

async function loadData(pointUrl, frameUrl, keyValueUrl) {
  let results = {
    sql: [],
    python: []
  };
  await $.getJSON(pointUrl)
    .then((data) => {
      results.sql[0] = data.performance.sql;
      results.python[0] = data.performance.python;
    });
  await $.getJSON(frameUrl)
    .then((data) => {
      results.sql[1] = data.performance.sql;
      results.python[1] = data.performance.python;
    });
  await $.getJSON(keyValueUrl)
    .then((data) => {
      results.sql[2] = data.performance.sql;
      results.python[2] = data.performance.python;
    });
  return results;
}

async function showTraWhole() {
  let trajectoryId = parseInt($('#input-traWhole').val());
  let data = await loadTraWhole(trajectoryId);
  showChart('traWhole', data);
}

function loadTraWhole(trajectoryId) {
  return loadData('/trajectory_point/' + trajectoryId,
                        '/trajectory_frame/' + trajectoryId,
                        '/trajectory_keyvalue/' + trajectoryId);
}