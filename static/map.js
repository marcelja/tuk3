// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">

var map, heatmap, paths = [], markers = [];
var play = false;

var gradient = [
  'rgba(0, 255, 255, 0)',
  'rgba(0, 255, 255, 1)',
  'rgba(0, 191, 255, 1)',
  'rgba(0, 127, 255, 1)',
  'rgba(0, 63, 255, 1)',
  'rgba(0, 0, 255, 1)',
  'rgba(0, 0, 223, 1)',
  'rgba(0, 0, 191, 1)',
  'rgba(0, 0, 159, 1)',
  'rgba(0, 0, 127, 1)',
  'rgba(63, 0, 91, 1)',
  'rgba(127, 0, 63, 1)',
  'rgba(191, 0, 31, 1)',
  'rgba(255, 0, 0, 1)'
  ]

window.onload = function() {
  loadScript();
  initSlider();
  loadProfitTable();
}

function initSlider() {
  let timeSlider = $('#time-slider .slider');
  let granularitySlider = $('#granularity-slider .slider');
  timeSlider.val(0);
  granularitySlider.val(6);
  timeSlider.on('change', () => {
    onSliderChanged();
  });
  granularitySlider.on('change', () => {
    onSliderChanged();
  });
}

function onSliderChanged() {
  let timeValue = parseInt($('#time-slider .slider').val());
  let granularityValue = parseInt($('#granularity-slider .slider').val());
  let mapValue = $('#heatmap-select').val();
  
  // update label
  $('#time-frame').text(Math.floor(timeValue / 6) + ' : ' + timeValue % 6 + '0');
  $('#granularity-slider .slider-label').text('Granularity: ' + granularityValue);

  // get data
  loadHeatmap(mapValue, timeValue, granularityValue);
}

function autoPlay() {
  play = !play;
  $('#btn-autoplay').text(play ? '❙ ❙' : '▶');
  let timeValue = parseInt($('#time-slider .slider').val());
  runLoop(timeValue);
}

function runLoop(timeValue) {
  timeValue = (timeValue + 1) % 143;
  $('#time-frame').text(Math.floor(timeValue / 6) + ' : ' + timeValue % 6 + '0');
  let granularityValue = parseInt($('#granularity-slider .slider').val());
  document.getElementsByClassName('slider')[0].value = timeValue;
  let mapValue = $('#heatmap-select').val();


  setTimeout(function(){

    loadHeatmap(mapValue, timeValue, granularityValue);

  if (play) runLoop(timeValue);
  }, 300);

}

function formatHeatmapData(rawData) {
  return rawData.map((point) => {
    return {location: new google.maps.LatLng(point[0], point[1]), weight: point[2]}
  })
}

function initMap() {
  let shenzhenCoords = {
    lat: 22.5497519,
    lng: 113.9824022
  }
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 12,
    center: shenzhenCoords,
    mapTypeId: 'satellite'
  });

  heatmap = new google.maps.visualization.HeatmapLayer({
    map: map,
    gradient: gradient,
    radius: 20
  });
}

function loadHeatmap(mapType, time, granularity) {
  let url = (function (mapType) {
    switch (mapType) {
      case 'all':
        return '/timeframe_granularity_heatmap/' + time + '/' + granularity
        break;
      case 'pickup':
        return '/changepoints/pickup/' + time + '/' + granularity
        break;
      case 'dropoff':
        return '/changepoints/dropoff/' + time + '/' + granularity
        break;
    }
  })(mapType);

  let startTime = new Date().getTime();
  $.getJSON(url, (data) => {
    let loadingTime = new Date().getTime() - startTime;
    $('#loadingTime').text(loadingTime + ' ms');
    let heatmapData = formatHeatmapData(data.result);
    heatmap.setData(heatmapData);
  });
}

function toggleHeatmap() {
  heatmap.setMap(heatmap.getMap() ? null : map);
}

function showHeatmap() {
  let value = $('#heatmap-select').val();
  if (value === 'none') {
    heatmap.setMap(null);
  }
  else {
    if (!heatmap.map) {
      heatmap.setMap(map);
    }
    onSliderChanged();
  }
}

function changeGradient() {
  heatmap.set('gradient', heatmap.get('gradient') ? null : gradient);
}

function changeRadius() {
  heatmap.set('radius', heatmap.get('radius') ? null : 20);
}

function changeOpacity() {
  heatmap.set('opacity', heatmap.get('opacity') ? null : 0.2);
}

function onInputTrajectoryKeypress(event) {
  let enterCode = 13;
  if (event.charCode === enterCode) {
    let trajectoryId = parseInt(event.target.value);
    drawRoute(trajectoryId);
  }
}

function onDrawRouteClick() {
  let trajectoryId = parseInt($('#input-trajectory').val());
  drawRoute(trajectoryId);
}

function toggleProfitOverlay() {
  if ($('#profit-overlay-btn').hasClass('active')) {
    $('#profit-overlay').removeClass('visible');
    $('#profit-overlay').addClass('hidden');
  } 
  else {
    $('#profit-overlay').removeClass('hidden');
    $('#profit-overlay').addClass('visible');
  }
}

function calculateTimeDifference(startTime, endTime) {
  var start = startTime.split(":");
  var end = endTime.split(":");
  var startMin = Number(start[0]) * 60 + Number(start[1]);
  var endMin = Number(end[0]) * 60 + Number(end[1]);
  return endMin - startMin;
}

function addInformation(position, startTime, endTime, distance) {
  var diff = calculateTimeDifference(startTime, endTime);
  var km = Math.round(2.4*distance/1000);
  var waiting = Math.round(diff * 0.1 / 60 * 48);

  var infowindow = new google.maps.InfoWindow({
    content: `start: ${startTime}, 
    end: ${endTime}<br>distance: ${Math.round(distance/100)/10} km<br>
    est. price: 11.00¥ + ${km}¥ (km) + ${waiting}¥ (waiting) 
    = ${11+km+waiting}¥`
  });

  var icon = {
    url: "static/yuan.png",
    scaledSize: new google.maps.Size(30, 30)
  };

  var marker = new google.maps.Marker({
    position: position,
    map: map,
    title: 'Taxi',
    icon: icon
  });
  marker.addListener('click', function() {
    infowindow.open(map, marker);
  });
  markers.push(marker);
}

function addPolyline(coordinates, occupancy, startTime, endTime) {
  if (coordinates.length == 0) return;
  var color = occupancy == 0 ? '#FF0000' : '#33cc33';

  var path = new google.maps.Polyline({
    path: coordinates,
    geodesic: true,
    strokeColor: color,
    strokeOpacity: 1.0,
    strokeWeight: 3,
    geodesic: true,
    icons: [{
      icon: {path: google.maps.SymbolPath.FORWARD_OPEN_ARROW},
      offset: '100%',
      repeat: '120px'
    }]
  });

  var distance = google.maps.geometry.spherical.computeLength(path.getPath());
  if (occupancy == 1) {
    // add a text with information about the price
    var markerId = markers.length;
    addInformation(coordinates[coordinates.length - 1], startTime, endTime, distance);

    google.maps.event.addListener(path, 'click', function(h) {
      // trigger click on marker for current path
      google.maps.event.trigger(markers[markerId], 'click', {});
    });
  }

  path.setMap(map);
  paths.push(path);
}

function drawRoute(id) {
  if (!id) {
    return;
  }
  
  $.getJSON('/route/' + id, (routeData) => {
    if (routeData.length <= 2) {
      return;
    }
    clearPaths();
    var occupancy = null;
    var startTime = routeData[0][0];
    var endTime;
    var coordinates = [];
    for (var i = 0; i < routeData.length; i++) {
      if (occupancy == null || occupancy != routeData[i][3] || i == routeData.length - 1) {
        endTime = routeData[i][0]
        coordinates.push({lat: routeData[i][2], lng: routeData[i][1]});
        addPolyline(coordinates, occupancy, startTime, endTime);
        startTime = routeData[i][0];
        occupancy = routeData[i][3];
        coordinates = [];
      }
      coordinates.push({lat: routeData[i][2], lng: routeData[i][1]});
    }
  });
}

function clearPaths() {
  for (let marker of markers) {
    marker.setMap(null)
    marker = null;
  }
  markers = [];
  for (let path of paths) {
    path.setMap(null);
    path = null;
  }
  markers = [];
}

function loadProfitTable() {
  $.getJSON('/profit', (profitData) => {
    let table = $('#profit-table')[0];
    for(entry of profitData) {
      let row = table.tBodies[0].insertRow(table.length);
      let trajectoryID = document.createTextNode(entry[0]);
      let totalProfit = document.createTextNode(entry[1].toFixed(2));
      let numTours = document.createTextNode(entry[4] / 11);
      let distance = document.createTextNode((entry[2] / 2.4).toFixed(1));

      row.insertCell(0).appendChild(trajectoryID);
      row.insertCell(1).appendChild(totalProfit);
      row.insertCell(2).appendChild(numTours);
      row.insertCell(3).appendChild(distance);
    }

    $(table).DataTable({
      paging: false,
      searching: false,
      bInfo: false,
    }).order([1, 'desc']).draw();

    $('#profit-table td').on('click', (event) => {
      let trajectoryId = parseInt($(event.target).parent().find('td:first-child').text());
      drawRoute(trajectoryId);
      $('#profit-overlay-btn').click();
    });
  });
}

function loadScript() {
  $.getJSON("static/api_key.json", function(json) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://maps.googleapis.com/maps/api/js?key=' + json['api_key'] + '&libraries=visualization,geometry&callback=initMap';
    
    document.body.appendChild(script);
    // wait for google script to load
    setTimeout(function(){
      onSliderChanged();
    }, 2000);
  });
}
