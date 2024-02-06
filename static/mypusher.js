// Enable pusher logging - don't include this in production
//Pusher.logToConsole = true;

function getconfig()
{
    fetch('/getconfig', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json'
    },
    }).then(response => {
        if (response.ok) {
            // If the response status is in the 200-299 range, it means the request was successful.
            return response.json(); // Parse the response as JSON
        } else {
            // Handle errors or non-successful responses here
            throw new Error('Request failed with status: ' + response.status);
        }
    }).then(data => {

        console.log(data);

        // TODO: get pusher key from my server
        var pusher = new Pusher(data["PUSHER_API_KEY"], {
            cluster: 'us2'
        });
    
        var channel = pusher.subscribe('lineupgen-shareduser');
        channel.bind('game-changed', function(data) {
            // if this game_id is the one I have open then update it
            var current_game_id = document.getElementById('current_game_id');
            //alert(data.game_id + current_game_id.value);
            if (current_game_id.value == data.game_id)
            {
            console.log("other person edited - updating")
            getserverdata(data.game_id);
            }
    
        });


    }).catch(error => {
        console.error(error);
    });}
