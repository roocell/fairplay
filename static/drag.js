function getshifts()
{
  var data = new Array();

  // build data of the shifts on screen
  // to send back to python
  var shifts = document.querySelectorAll(".shift");
  shifts.forEach(function(shift) {
    // inside each shift is a player class
    var parray = new Array();
    var players = shift.querySelectorAll(".player");
        players.forEach(function(player) {
          parray.push({
            "name" : player.id
              })
        });
    data.push(parray)
  });
  return data;
}

function updateDomWithShifts(data)
{
  console.log(data);

  // update the DOM with the new shifts
  var container = document.getElementById("container");
  container.innerHTML = "";

  // update the roster in the DOM with the players again
  var rosterdiv = document.createElement('div');
  rosterdiv.className = "shift";
  rosterdiv.id = "roster";
  var rheader = document.createElement('h3');
  rheader.className = "heading";
  rheader.innerHTML = "Roster";
  rosterdiv.appendChild(rheader);
  
  var playersData = JSON.parse(data.players);
  playersData.forEach(function(player) {
    var playerp = document.createElement("p");
    playerp.classList.add("player");
    playerp.setAttribute("draggable", "true");
    playerp.id = player.name;
    playerp.innerHTML = player.number + " " + player.name + " " + player.shifts;
    playerp.setAttribute('data-backgroundColor', player.colour);
    rosterdiv.appendChild(playerp);
  });
  container.appendChild(rosterdiv);

  var i = 0;
  var shiftsData = JSON.parse(data.shifts);
  shiftsData.forEach(function(shift) {
    i++;
    var shiftdiv = document.createElement('div');
    shiftdiv.className = "shift";
    shiftdiv.id = "shift" + i;

    var header = document.createElement('h3');
    header.className = "heading";
    header.innerHTML = "Shift" + i;
    shiftdiv.appendChild(header);
    
    shift.forEach(function(player) {
      var playerp = document.createElement('p');
      playerp.className = "player";
      playerp.draggable = "true";
      playerp.id = player.name;
      playerp.innerHTML = player.number + " " + player.name + " " + player.shifts;
      playerp.setAttribute('data-backgroundColor', player.colour);
      playerp.setAttribute('data-doubleshift', player.doubleshifts[i-1]);
      
      shiftdiv.appendChild(playerp);
    });
    container.appendChild(shiftdiv);
  });
  setupDraggablesAndDroppables();
}

function updateshifts()
{
  // Make a POST request to your Flask route with the JSON data
  fetch('/updateshifts', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(getshifts())
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
        updateDomWithShifts(data);
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });

}

function getdata()
{
  fetch('/getdata', {
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
        updateDomWithShifts(data);
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });
}

function runfairplay()
{
  fetch('/runfairplay', {
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
        updateDomWithShifts(data);
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });
}

// need to define the listeners are separate function rather than inline
// because when we clone a node only intrinsic (set in HTML tag) listeners are copied
function playerDragStart()
{
  var player = this;
  if (player.parentElement.id == "roster") {
      player.dataset.fromRoster = true;
      // find index of child in parent - so we can clone in same position
      for (var i = 0; i < player.parentElement.children.length; i++) {
        if (player.parentElement.children[i] == player) {
          player.dataset.rosterPosition = i;
          break;
        }
      }
  } else {
    player.dataset.fromRoster = false;
  }
  player.classList.add("is-dragging");
  player.style.backgroundColor = "rgb(50, 50, 50)";
  //console.log(player)
}

function playerDragEnd(event)
{
  var player = this;
  player.classList.remove("is-dragging");
  player.style.backgroundColor = player.getAttribute('data-backgroundColor');

  // if it's the roster - clone it so we don't remove it from the roster
  if (player.dataset.fromRoster == "true") {
    var rosterdiv = document.getElementById("roster");
    const playerClone = player.cloneNode(true);
    // need to add the listeners manually on a cloned node
    // (if not specified instrinicly)
    playerClone.addEventListener("dragstart", playerDragStart);
    playerClone.addEventListener("dragend", playerDragEnd);

    var referenceElement = rosterdiv.children[player.dataset.rosterPosition];
    rosterdiv.insertBefore(playerClone, referenceElement);
  }

  event.preventDefault();
  updateshifts();  
}

function setupDraggablesAndDroppables()
{
  const draggables = document.querySelectorAll(".player");
  const droppables = document.querySelectorAll(".shift");
  
  draggables.forEach((player) => {
    player.style.backgroundColor = player.getAttribute('data-backgroundColor');
    if ( player.getAttribute('data-doubleshift') == 1)
    {
      player.classList.add("is-doubleshift");
    } else {
      player.classList.remove("is-doubleshift");
    }
    player.addEventListener("dragstart", playerDragStart);
    player.addEventListener("dragend", playerDragEnd);
    // tried 'drop' but you can drag your item into a 
    // list but then mouse our of the list and then the
    // drop event doesn't trigger
    // dragend works better
    //player.addEventListener("drop", (event) => {  
    //});
  });
  
  droppables.forEach((zone) => {
    zone.addEventListener("dragover", (e) => {
      e.preventDefault();
      const curPlayer = document.querySelector(".is-dragging");

      // you can't drop an identical player
      var shift = zone;
      const players = shift.querySelectorAll('.player');
      let playerIsDup = false;
      players.forEach((player) => {
        if (player.id == curPlayer.id)
        {
          playerIsDup = true;
        }

      });
      if (playerIsDup) {
        return;
      }
      
      const bottomPlayer = insertAbovePlayer(zone, e.clientY);
      //console.log(curPlayer)

      if (!bottomPlayer) {
        zone.appendChild(curPlayer);
      } else {
        zone.insertBefore(curPlayer, bottomPlayer);
      }
    
    });
  });
  
  const insertAbovePlayer = (zone, mouseY) => {
    const els = zone.querySelectorAll(".player:not(.is-dragging)");
  
    let closestPlayer = null;
    let closestOffset = Number.NEGATIVE_INFINITY;
  
    els.forEach((player) => {
      const { top } = player.getBoundingClientRect();
  
      const offset = mouseY - top;
  
      if (offset < 0 && offset > closestOffset) {
        closestOffset = offset;
        closestPlayer = player;
      }
    });
  
    return closestPlayer;
  };

}
