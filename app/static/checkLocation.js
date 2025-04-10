document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    if (navigator.geolocation) {
        console.log('Geolocation is supported');
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        console.log('Geolocation is not supported');
        document.getElementById("locationPrompt").innerText = "Geolocation is not supported by this browser.";
    }
});

function showPosition(position) {
    console.log('Position obtained:', position);
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const austinLat = 30.2672;
    const austinLon = -97.7431;
    const threshold = 0.1;

    const locationButton = document.getElementById("locationButton");
    const locationPrompt = document.getElementById("locationPrompt");

    if (Math.abs(lat - austinLat) < threshold && Math.abs(lon - austinLon) < threshold) {
        console.log('User is in Austin');
        locationPrompt.innerHTML = 'Not sure what buses are near you? Click <span id="getLocationBtn">here</span> to find out!';
        document.getElementById("getLocationBtn").addEventListener('click', function() {
            console.log("getLocationBtn clicked");
            loadScript("{{ url_for('static', filename='location.js') }}");
        });
    } else {
        console.log('User is not in Austin');
        locationPrompt.innerHTML = 'Hey, we noticed you aren\'t in Austin, click <span id="setLocationButton">here</span> to spoof your location to be in Austin.';
        locationButton.innerText = "Spoof Location to Austin";
        locationButton.classList.add("blue-button");
        locationButton.setAttribute("id", "setLocationButton");
        document.getElementById("setLocationButton").addEventListener('click', function() {
            loadScript("{{ url_for('static', filename='setLocation.js') }}");
        });
    }
}

function showError(error) {
    console.log('Error occurred:', error);
    switch(error.code) {
        case error.PERMISSION_DENIED:
            document.getElementById("locationPrompt").innerText = "User denied the request for Geolocation.";
            break;
        case error.POSITION_UNAVAILABLE:
            document.getElementById("locationPrompt").innerText = "Location information is unavailable.";
            break;
        case error.TIMEOUT:
            document.getElementById("locationPrompt").innerText = "The request to get user location timed out.";
            break;
        case error.UNKNOWN_ERROR:
            document.getElementById("locationPrompt").innerText = "An unknown error occurred.";
            break;
    }
}

function loadScript(url) {
    console.log("Loading script:", url);
    const script = document.createElement('script');
    script.src = url;
    script.defer = true;
    document.body.appendChild(script);
}