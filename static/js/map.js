var map, initialLocation;
var marker, circle;
var currentLat, currentLng, currentRad;

function getRadius() {
    newVal = $("#slider").val();
    $('#sliderLabel').text(newVal);
    updateCircle(newVal * 1000);
}

function updateCircle(radius) {
    if (circle == undefined) {
        circle = new google.maps.Circle({
            map: map,
            radius: radius,
            strokeColor: '#EA4335',
            strokeOpacity: 1,
            strokeWeight: 2,
            fillColor: '#EA4335',
            fillOpacity: 0.2
        });
        circle.bindTo('center', marker, 'position');
        marker.circle = circle;
    } else {
        circle.setRadius(radius);
    }
    currentRad = radius;
    info();
}

function updateMarker(latLng) {
    if (marker == undefined) {
        marker = new google.maps.Marker({
            center: latLng,
            position: latLng,
            map: map,
            draggable: true,
            animation: google.maps.Animation.DROP,
            scrollwheel: true
        });
    }
    else {
        marker.setPosition(latLng);
        infoWindow.close()
    }
    map.panTo(latLng);
    currentLat = latLng.lat;
    currentLng = latLng.lng;
    info();
}

function info() {
    console.log(
        'Lat: ' + currentLat + ', ' +
        'Lng: ' + currentLng + ', ' +
        'Rad: ' + currentRad);
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
    infoWindow.open(map);
}

function init() {
    // var rome = new google.maps.LatLng(41.9100711, 12.5359979);
    var initialRadius = 5;
    $('#slider').val(initialRadius);
    $('#sliderLabel').text(initialRadius);
    currentRad = initialRadius * 1000;

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        clickableIcons: false,
    });
    infoWindow = new google.maps.InfoWindow;

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {

            var latLng = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            map.setCenter(latLng);
            updateMarker(latLng);
            updateCircle(currentRad);
            infoWindow.setPosition(latLng);
            infoWindow.setContent('You are here.');
            infoWindow.open(map, marker);

            marker.addListener('dragend', function () {
                infoWindow.close()
            });

            google.maps.event.addListener(map, 'click', function (event) {
                handlePositionEvent(event.latLng);
            });

            google.maps.event.addListener(marker, 'dragstart', function (event) {
            });

            google.maps.event.addListener(marker, 'dragend', function (event) {
                handlePositionEvent(event.latLng);
            });


            function handlePositionEvent(latLng) {
                var latLngObj = {
                    lat: latLng.lat(),
                    lng: latLng.lng()
                }
                updateMarker(latLngObj);
            }

        }, function () {
            handleLocationError(true, infoWindow, map.getCenter());
        });
    } else {
        handleLocationError(false, infoWindow, map.getCenter());
    }
}