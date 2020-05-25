let best_position = null;

function init_map() {
  let map = new google.maps.Map($("#map")[0], {
    center: {lat: 48.7071075, lng: 19.7599799},
    zoom: 8,
    streetViewControl: false,
    fullscreenControl: false,
    mapTypeId: 'hybrid'
  });
  let marker = new google.maps.Marker({
    position: {lat: 48.7071075, lng: 19.7599799}
  });

  function success_cb(position) {
    $("#overlay").hide();
    $("#send-button").prop("disabled", false);
    if (best_position === null || best_position.accuracy > position.coords.accuracy) {
      best_position = {lat: position.coords.latitude, lng: position.coords.longitude, accuracy: position.coords.accuracy};
    }
    let geo = {lat: position.coords.latitude, lng: position.coords.longitude};
    map.setCenter(geo);
    marker.setMap(map);
    marker.setPosition(geo);
    if (map.getZoom() < 17) {
      map.setZoom(17);
    }
  }

  function error_cb(error) {
    console.log(error);
    if (best_position === null) {
      if (error.code === 1) {
        $("#overlay div").hide();
        $("#overlay .allow").show();
      } else if (error.code === 2) {
        $("#overlay div").hide();
        $("#overlay .unavailable").show();
      }
    }
  }

  if (!navigator.geolocation) {
  } else {
    navigator.geolocation.watchPosition(success_cb, error_cb, {"enableHighAccuracy": true});
  }
}

function submit() {
  if (best_position !== null) {
    $("#lat").val(best_position.lat);
    $("#lng").val(best_position.lng);
    $("#form").submit();
  }
}
