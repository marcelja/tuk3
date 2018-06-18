charts = {};

window.onload = function () {
  initCharts();
}

function initCharts() {
  let traWholeCtx = document.getElementById('chart-traWhole');
  charts.traWhole = new Chart(traWholeCtx, {
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

function clearDataSets(chart) {
  for (dataset of charts[chart].data.datasets) {
    dataset.data = [];
  }
}

async function showTraWhole() {
  let trajectoryId = parseInt($('#input-traWhole').val());
  let data = await loadTraWhole(trajectoryId);
  clearDataSets('traWhole');
  charts.traWhole.data.datasets[0].data = data.sql;
  charts.traWhole.data.datasets[1].data = data.python;
  charts.traWhole.update();
}

async function loadTraWhole(trajectoryId) {
  let results = {
    sql: [],
    python: []
  };
  await $.getJSON('/trajectory_point/' + trajectoryId)
    .then((data) => {
      results.sql[0] = data.performance.sql;
      results.python[0] = data.performance.python;
    });
  await $.getJSON('/trajectory_frame/' + trajectoryId)
    .then((data) => {
      results.sql[1] = data.performance.sql;
      results.python[1] = data.performance.python;
    });
  await $.getJSON('/trajectory_keyvalue/' + trajectoryId)
    .then((data) => {
      results.sql[2] = data.performance.sql;
      results.python[2] = data.performance.python;
    });

  return results;
}