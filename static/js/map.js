var map, initialLocation;
var marker, circle, infoWindow;
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
    updateForm();
}

function handlePositionEvent(latLng) {
    var latLngObj = {
        lat: latLng.lat(),
        lng: latLng.lng()
    }
    updateMarker(latLngObj);
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
    updateForm();
}

function updateForm() {
    $('input#lat').val(currentLat);
    $('input#lng').val(currentLng);
    $('input#rad').val(currentRad / 1000 ); // wikibase:radius is already in kilometers
    console.log(
        'Lat: ' + currentLat + ', ' +
        'Lng: ' + currentLng + ', ' +
        'Rad: ' + currentRad);
}

function init() {
    var initialRadius = 50;
    $('#slider').val(initialRadius);
    $('#sliderLabel').text(initialRadius);
    currentRad = initialRadius * 1000;

    var args = {
        zoom: 8,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false,
        clickableIcons: false,
    }

    var map_enabled = true;
    if ($("#js-map_enabled").attr('map_enabled') == 0)
        map_enabled = false;

    if (!map_enabled) {
        args.disableDefaultUI = true
        args.panControl = false
    }

    map = new google.maps.Map($('#map')[0], args);
    infoWindow = new google.maps.InfoWindow;
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var latLng = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            map.setCenter(latLng);
            if (map_enabled) {
                updateMarker(latLng);
                updateCircle(currentRad);
                infoWindow.setContent('You are here.');
                infoWindow.open(map, marker);
                $("#status").show().addClass('alert-success').text("We have placed you on the map based on your geolocation.")
                addListeners()
            } else {
                latLng.lat = parseFloat($("#js-map_enabled").attr('latitude'));
                latLng.lng = parseFloat($("#js-map_enabled").attr('longitude'));
                updateMarker(latLng);
                map.setOptions({ draggable: false, zoomControl: false, scrollwheel: false, disableDoubleClickZoom: true });
                map.setCenter(latLng);
            }
        }, function () {
            handleLocationError(true);
        });
    } else {
        handleLocationError(false);
    }

    function handleLocationError(browserHasGeolocation) {
        var rome = new google.maps.LatLng(41.902782, 12.496366);
        map.setCenter(rome);
        handlePositionEvent(rome);
        updateCircle(currentRad);
        infoWindow.setContent('You are here.');
        infoWindow.open(map, marker);
        $("#status").show().addClass('alert-warning').text("Geolocation service failed, We've placed you in Rome.")
    }

    function addListeners() {
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
    }
}