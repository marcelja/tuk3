// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">

var map, heatmap;

window.onload = function() {
  loadScript();
  initSlider();
}

function initSlider() {
  let timeSlider = $('#time-slider .slider');
  let granularitySlider = $('#granularity-slider .slider');
  timeSlider.on('input', () => {
    onSliderChanged();
  });
  granularitySlider.on('input', () => {
    onSliderChanged();
  });
  timeSlider.val(0);
  granularitySlider.val(6);
  onSliderChanged();
}

function onSliderChanged() {
  let timeValue = parseInt($('#time-slider .slider').val());
  let granularityValue = parseInt($('#granularity-slider .slider').val());
  
  // update label
  $('#time-slider .slider-label').text(timeValue + ' h');
  $('#granularity-slider .slider-label').text('Granularity: ' + granularityValue);

  // get data
  let frame = timeValue * 6; // each frame is 10 minutes
  $.getJSON('/timeframe_granularity/' + frame + '/0/' + granularityValue, (data) => {
    let heatmapData = formatHeatmapData(data);
    heatmap.setData(heatmapData);
  });
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
    data: getPoints(),
    map: map
  });
}

function toggleHeatmap() {
  heatmap.setMap(heatmap.getMap() ? null : map);
}

function changeGradient() {
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
  heatmap.set('gradient', heatmap.get('gradient') ? null : gradient);
}

function changeRadius() {
  heatmap.set('radius', heatmap.get('radius') ? null : 20);
}

function changeOpacity() {
  heatmap.set('opacity', heatmap.get('opacity') ? null : 0.2);
}

function getPoints() {
  return [
  {location: new google.maps.LatLng(37.782, -122.447), weight: 0.5},
  new google.maps.LatLng(37.782, -122.445),
  {location: new google.maps.LatLng(37.782, -122.443), weight: 2},
  {location: new google.maps.LatLng(37.782, -122.441), weight: 3},
  {location: new google.maps.LatLng(37.782, -122.439), weight: 2},
  new google.maps.LatLng(37.782, -122.437),
  {location: new google.maps.LatLng(37.782, -122.435), weight: 0.5},

  {location: new google.maps.LatLng(37.785, -122.447), weight: 3},
  {location: new google.maps.LatLng(37.785, -122.445), weight: 2},
  new google.maps.LatLng(37.785, -122.443),
  {location: new google.maps.LatLng(37.785, -122.441), weight: 0.5},
  new google.maps.LatLng(37.785, -122.439),
  {location: new google.maps.LatLng(37.785, -122.437), weight: 2},
  {location: new google.maps.LatLng(37.785, -122.435), weight: 3}
  ];
}

function addInformation(position, startTime, endTime, distance) {
  var infowindow = new google.maps.InfoWindow({
    content: `start: ${startTime}, end: ${endTime}<br>distance: ${Math.round(distance/100)/10} km`
  });
  var marker = new google.maps.Marker({
    position: position,
    map: map,
    title: 'Taxi'
  });
  marker.addListener('click', function() {
    infowindow.open(map, marker);
  });
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
    addInformation(coordinates[parseInt(coordinates.length / 2)], startTime, endTime, distance)
  }

  path.setMap(map);
}

function drawRoute(id) {
  $.getJSON('/route/' + id, (routeData) => {
    if (routeData.length <= 2) {
      return;
    }
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

function loadScript() {
  $.getJSON("static/api_key.json", function(json) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://maps.googleapis.com/maps/api/js?key=' + json['api_key'] + '&libraries=visualization,geometry&callback=initMap';
    
    document.body.appendChild(script);
    // wait for google script to load
    setTimeout(function(){
      drawRoute(22223);
    }, 2000);
  });
}
