let best_position = null;
let watch_id = null;
let accuracy_bound = 0;
let accuracy_timeout = 0;


function enable_submit() {
    if (best_position !== null) {
        $("#place-submit").attr("disabled", false);
        $("#place-accuracy .spinner").removeClass("fa-pulse").removeClass("fa-spinner").addClass("fa-check-circle");
    }
}

function success_cb(position) {
    console.log(position);
    $("#place-part .doing").hide(200);
    $("#place-part .denied").hide(200);
    $("#place-part .unavailable").hide(200);
    $("#place-part .unsupported").hide(200);
    $("#place-part .available").show(200);
    $("#place-accuracy .spinner").show();
    if (best_position === null) {
        $("#place-head").removeClass("gray");
        $("#try-body").slideUp(300);
        $("#place-body").slideDown(300);
    }
    $("#place-try").attr("disabled", true);
    if (best_position === null || best_position.accuracy > position.coords.accuracy) {
        best_position = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
        };
        $("#lat").val(best_position.lat).text(best_position.lat);
        $("#lng").val(best_position.lng).text(best_position.lng);
        $("#place-accuracy span").text(Math.round(position.coords.accuracy) + " m");
        if (position.coords.accuracy <= accuracy_bound) {
            enable_submit();
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
    let bad = 0;
    $("#address-part input").each(function (i, elem) {
        if ($(elem).val() === "") {
            $(elem).addClass("govuk-input--error");
            $(elem).parents(".govuk-form-group").addClass("govuk-form-group--error");
            $(elem).siblings("span").show(100);
            bad++;
        } else {
            $(elem).removeClass("govuk-input--error");
            $(elem).parents(".govuk-form-group").removeClass("govuk-form-group--error");
            $(elem).siblings("span").hide(100);
        }
    });
    if (bad !== 0) {
        event.preventDefault();
        return;
    }
    event.preventDefault();
    $("#try-head").removeClass("gray");
    $("#address-body").slideUp(300);
    $("#try-body").slideDown(300);
    setTimeout(enable_submit, accuracy_timeout);
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
        $("#place-part .doing").show(200);
        watch_id = navigator.geolocation.watchPosition(success_cb, error_cb, {
            "enableHighAccuracy": true,
            "timeout": 3000
        });
    }
}

function place_submit(event) {
    console.log(event);
    if (best_position !== null) {
        $("#form").submit();
    }
}

