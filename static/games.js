function saveGameButtonClicked()
{
    var gamename = "";

    var data = { "name" : gamename };
    var datastr = JSON.stringify(data);
  
    fetch('/savegame', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: datastr
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
            games = JSON.parse(data.games);
            console.log(games)
            updateDomGames(games);
            var selectElement = document.getElementById("games");
            selectElement.value = games[games.length-1].id;
          } else {
              console.log(data.games)
          }
      }).catch(error => {
          // Handle any network or request-related errors here
          console.error(error);
      });
}
function deleteGameButtonClicked()
{
    var selectElement = document.getElementById("games");
    var data = { "game_id" : selectElement.value };
    var datastr = JSON.stringify(data);
    // can't delete default(1)
    if (selectElement.value == 1)
    {
        alert("Can't delete default(1) game");
        return;
    }

    fetch('/deletegame', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: datastr
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
              // reset to default
              getserverdata(1); // game_id=1 is default
              getgames();
          } else {
              console.log(data.games)
          }
      }).catch(error => {
          // Handle any network or request-related errors here
          console.error(error);
      });
}

function updateDomGames(games)
{
    var selectElement = document.getElementById("games");
    selectElement.innerHTML = '';
    for (var i = 0; i < games.length; i++) {
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
            updateDomGames(JSON.parse(data.games));
        } else {
            console.log(data.games)
        }
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });

}

function handleGameChange(selectElement)
{
    game_id = selectElement.value;
    getserverdata(game_id);
}