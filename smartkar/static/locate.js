let best_position = null;
let watch_id = null;

function success_cb(position) {
    console.log(position);
    $("#place-part .denied").hide(200);
    $("#place-part .unavailable").hide(200);
    $("#place-part .unsupported").hide(200);
    $("#place-part .available").show(200);
    $("#place-try").attr("disabled", true);
    if (best_position === null || best_position.accuracy > position.coords.accuracy) {
        best_position = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
        };
        $("#place-accuracy span").text(position.coords.accuracy + " m");
        if (position.coords.accuracy <= 150) {
            $("#place-submit").attr("disabled", false);
        }
    }
}

function error_cb(error) {
    console.log(error);
    if (best_position === null) {
        if (error.code === 1) {
            $("#place-part .denied").show(200);
        } else if (error.code === 2 || error.code === 3) {
            $("#place-part .unavailable").show(200);
        }
    }
}

function address_submit(event) {
    console.log(event);
    if (type === "b") {
        event.preventDefault();
        $("#address-part").slideToggle();
        $("#place-part").slideToggle();
    }
}

function place_try(event) {
    console.log(event);
    event.preventDefault();
    if (!navigator.geolocation) {
        $("#place-part .unsupported").show();
    } else {
        if (watch_id !== null) {
            navigator.geolocation.clearWatch(watch_id);
        }
        watch_id = navigator.geolocation.watchPosition(success_cb, error_cb, {"enableHighAccuracy": true, "timeout": 1000});
    }
}

function place_submit(event) {
    console.log(event);
    if (best_position !== null) {
        $("#lat").val(best_position.lat);
        $("#lng").val(best_position.lng);
        $("#form").submit();
    }
}

