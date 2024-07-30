let isAustin = false;
let isSpoofed = false

document.addEventListener("DOMContentLoaded", function() {
    const spoofButton = document.getElementById("spoofButton");
    const austinCoords = { latitude: 30.2672, longitude: -97.7431 };
    const tolerance = 0.1; // tolerance for comparing coordinates

    // Function to check if coordinates are within tolerance range
    function isNotInAustin(position) {
        const { latitude, longitude } = position.coords;
        console.log(Math.abs(latitude - austinCoords.latitude) > tolerance)
        return Math.abs(latitude - austinCoords.latitude) > tolerance ||
               Math.abs(longitude - austinCoords.longitude) > tolerance;
    }

    // Check if the location has been spoofed before
    const isSpoofed = localStorage.getItem('isSpoofed') === 'true';

    // Get user's current location
    navigator.geolocation.getCurrentPosition(function(position) {

        if (isNotInAustin(position) && !isSpoofed) {
            console.log("user not in austin")
            spoofButton.style.display = 'block'; // Show button if user is not in Austin and location is not spoofed
            localStorage.setItem('isAustin', 'false');
            localStorage.setItem('isSpoof', 'true');
            

        } else if (isNotInAustin(position) && isSpoofed) {
            console.log("user not in austin but is spoofed")
            spoofButton.style.display = 'block'; // Show button if user is not in Austin and location is not spoofed
            localStorage.setItem('isAustin', 'false');

        }
        
        else {
            console.log("user in austin")

            spoofButton.style.display = 'none'; // Hide button if user is in Austin or location is spoofed
            isAustin = true; // Set isAustin to true if location is in Austin
            localStorage.setItem('isAustin', 'true');

        }
    }, function(error) {
        console.error("Error getting location: ", error);
    });

    spoofButton.addEventListener("click", function() {
        // Spoof location coordinates for Austin, TX
        const spoofedPosition = {
            coords: {
                latitude: 30.2672,
                longitude: -97.7431
            }
        };

        // Mock the Geolocation API
        navigator.geolocation.getCurrentPosition = function(success, error) {
            success(spoofedPosition);
        };

        // Set the spoofed state in local storage
        localStorage.setItem('isSpoofed', 'true');

        alert("Your location has been spoofed to Austin, TX.");
        isAustin = false; // Set isAustin to false because the location is spoofed
        window.location.reload(); // Refresh the page
    });
});
