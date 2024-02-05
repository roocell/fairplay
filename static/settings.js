function addPlayer() {
  player_number = document.getElementById("player-number");
  player_name = document.getElementById("player-name");
  

  const number = player_number.value;
  const name = player_name.value;
  const rosterLane = document.getElementById("roster");

  if (!number || !name) return;

  // add player to the dom - then it'll get picked up when
  // we send data back to the server
  const newPlayer = document.createElement("p");
  newPlayer.classList.add("player");
  newPlayer.setAttribute("draggable", "true");
  newPlayer.innerText = number + " " + name;
  newPlayer.id = 0; // unknown at this point (this is from db)
  newPlayer.name = name
  newPlayer.number = number

  newPlayer.addEventListener("dragstart", () => {
    newPlayer.classList.add("is-dragging");
  });
 
  newPlayer.addEventListener("dragend", () => {
    newPlayer.classList.remove("is-dragging");
  });

  rosterLane.appendChild(newPlayer);

  player_number.value = "";
  player_name.value = "";

  // send roster back to server
  updatedata();
}


function generateSettingsDiv(shiftscontainer)
{
  var settingscontainer = document.createElement('div');
  settingscontainer.classList.add('settings');

  var header = document.createElement('h3');
  header.className = "heading";
  header.style.textAlign = "right";
  header.innerHTML = "Game Sharing List"
  settingscontainer.appendChild(header);

  shiftscontainer.appendChild(settingscontainer);
  settingscontainer.innerHTML += `
    <!-- some settings -->
    <form class="settings-form" id="settings-form">
      <input type="text" class="player-input" placeholder="share with <email>" id="share-email" />
      <button type="button" class="settings-button" onclick="addSharedUser()">+</button>
    </form>
    <div id="shared-user-list">
      
    </div>
    `
}

function updateSharedUsersInDom(data)
{
  sharediv = document.getElementById("shared-user-list");
  sharediv.innerHTML = "";

  console.log(data);
  var shared_users = JSON.parse(data.shared_users);

  shared_users.forEach(function(share_user) {
    var sharedusercontainer = document.createElement('div');
    sharedusercontainer.style.display = 'grid';
    sharedusercontainer.style.gridTemplateColumns = 'auto auto'; // two columns

    var shareduser = document.createElement('p');
    shareduser.className = "shareduser";
    shareduser.innerHTML = share_user.email;
    var button = document.createElement('button');
    button.className = "settings-button";
    button.setAttribute('type', 'button');
    button.textContent = '-';
    button.onclick = function() {
      deleteSharedUser(share_user.email);
    };
    sharediv.appendChild(sharedusercontainer);
    sharedusercontainer.appendChild(shareduser);
    sharedusercontainer.appendChild(button);

  });
  
}

function sendSettingsToServer(share_email)
{
  var data = {"share_email" : share_email};
  var datastr = JSON.stringify(data);
  console.log("datastr:" + datastr);
  //console.log(JSON.stringify(data));
  // Make a POST request to your Flask route with the JSON data
  showLoadingOverlay();
  fetch('/updatesettings', {
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
        updateSharedUsersInDom(data)
        hideLoadingOverlay();
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
        hideLoadingOverlay();
    });

}
function getSettingsFromServer()
{
  //showLoadingOverlay();
  fetch('/getsettings', {
      method: 'POST',
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
        updateSharedUsersInDom(data)
        //hideLoadingOverlay();
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
        //hideLoadingOverlay();
    });

}

function addSharedUser() {
  share_email = document.getElementById("share-email");

  // send list of shared emails
  // all games will be shared (for now)
  sendSettingsToServer(share_email.value);
}

function deleteSharedUser(share_email)
{
    var data = {"share_email" : share_email};
    var datastr = JSON.stringify(data);
    //showLoadingOverlay();
    fetch('/deleteshareduser', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: datastr,
  }).then(response => {
        if (response.ok) {
            // If the response status is in the 200-299 range, it means the request was successful.
            return response.json(); // Parse the response as JSON
        } else {
            // Handle errors or non-successful responses here
            throw new Error('Request failed with status: ' + response.status);
        }
    }).then(data => {
        updateSharedUsersInDom(data)
        //hideLoadingOverlay();
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
        //hideLoadingOverlay();
    });
}