charts = {};

window.onload = function () {
    initCharts();
}

function initCharts() {
    let traWholeCtx = document.getElementById('chart-tra-whole');
    charts.traWhole = new Chart(traWholeCtx, {
        type: 'bar',
        data: {
            labels: ["Points", "Frame", "Key-Value"],
            datasets: [{
                label: 'Execution time ms',
                data: [],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
    });

}