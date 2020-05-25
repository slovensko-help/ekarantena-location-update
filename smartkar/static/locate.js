function load() {
  function success_cb(position) {
    console.log(position);
  }

  function error_cb(error) {
    console.log(error);
  }

  if (!navigator.geolocation) {

  } else {
    navigator.geolocation.getCurrentPosition(success_cb, error_cb, {"enableHighAccuracy": true});
  }
}

$(document).ready(load)
