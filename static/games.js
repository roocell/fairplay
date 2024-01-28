function saveGameButtonClicked()
{
    showLoadingOverlay();

    var selectElement = document.getElementById("games");
    var gameTextField = document.getElementById("gamesInput");
    var data = { "game_id" : selectElement.value };
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
          hideLoadingOverlay();
          // Handle the JSON data received from the server
          if (data.status == "ok")
          {
            games = JSON.parse(data.games);
            console.log(games)
            updateDomGames(games);
            var selectElement = document.getElementById("games");
            selectElement.value = games[games.length-1].id;

            // update text field
            var gameTextField = document.getElementById("gamesInput");
            var selectedOption = selectElement.options[selectElement.selectedIndex];
            gameTextField.value = selectedOption.text;
          } else {
              console.log(data.games)
          }
      }).catch(error => {
        hideLoadingOverlay();
        // Handle any network or request-related errors here
          console.error(error);
      });
}
function deleteGameButtonClicked()
{
    showLoadingOverlay();

    var selectElement = document.getElementById("games");
    var data = { "game_id" : selectElement.value };
    var datastr = JSON.stringify(data);
    // can't delete default(1)
    if (selectElement.value == 1)
    {
        alert("Can't delete default(1) game");
        hideLoadingOverlay();
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
          hideLoadingOverlay();
          // Handle the JSON data received from the server
          if (data.status == "ok")
          {
              updateDomGames(data);
              // reset to default
              getgames(0)
              .then(()=> {
                getserverdata(game_id=document.getElementById("games").options[0].value); // default
              })
                .catch(error => {
                  // Handle errors here
                  console.error(error);
              });              
          } else {
              console.log(data.games)
          }
      }).catch(error => {
        hideLoadingOverlay();
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

function getgames(selectIndex)
{
  return fetch('/getgames', {
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

            // select default index
            var selectElement = document.getElementById("games");
            selectElement.selectedIndex = selectIndex

            // update text field
            var gameTextField = document.getElementById("gamesInput");
            var selectedOption = selectElement.options[selectElement.selectedIndex];
            gameTextField.value = selectedOption.text;

            // Disable the text input if the first option is selected, enable otherwise
            gameTextField.disabled = selectElement.selectedIndex === 0;

        } else {
            console.log(data.games)
        }
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });

}

function changeGameName(game_id, gamename)
{
    var data = { "game_id" : game_id, "name" : gamename };
    var datastr = JSON.stringify(data);
    console.log(data);

  fetch('/changegamename', {
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
        // success
        // updated the dropdown
        var selectElement = document.getElementById("games");
        getgames(selectElement.value-1);
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });
}


function handleGameChange(selectElement)
{
    game_id = selectElement.value;
    getserverdata(game_id);

    // update text field
    var gameTextField = document.getElementById("gamesInput");
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    gameTextField.value = selectedOption.text;

    // Disable the text input if the first option is selected, enable otherwise
    gameTextField.disabled = selectElement.selectedIndex === 0;
    
}

function handleGameNameChange(inputElement)
{
    // this is every keystroke
    //console.log("handleGameNameChange");
}

const form = document.getElementById("games-form");
form.addEventListener("submit", (e) => {
    e.preventDefault(); // prevent page reload like a default form submit would do

    var gameTextField = document.getElementById("gamesInput");
    var selectElement = document.getElementById("games");

    console.log("game form submit")

    // TODO: sanitize text
    if (gameTextField.value == "default")
    {
        alert("default is a reserved game name.");
        return;
    }

    changeGameName(selectElement.value, gameTextField.value);
});