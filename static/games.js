function addGameButtonClicked()
{
    console.log("addGameButtonClicked")
}
function removeGameButtonClicked()
{
    console.log("removeGameButtonClicked")
}

function updateDomGames(games)
{
    console.log(games.length)
    var selectElement = document.getElementById("games");

    for (var i = 0; i < games.length; i++) {
        console.log(i)
        var option = document.createElement("option");
        option.value = games[i].id;
        option.text = games[i].name;
        selectElement.add(option);
    }
}

function getgames()
{
  fetch('/getgames', {
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
        // Handle the JSON data received from the server
        if (data.status == "ok")
        {
            updateDomGames(data);
        } else {
            console.log(data.games)
        }
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });

}