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
    playerp.setAttribute("isDragging", "false");
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

function playerTouchStart(e)
{
  try {
    var player = this;
    // have to move the player div manually on mobile
    e.preventDefault(); // Prevent default touch events (e.g., scrolling)
    player.setAttribute('isDragging', "true");
  
    // Get the initial touch position
    const touch = e.changedTouches[0];
    const offsetX = touch.clientX - 30;
    const offsetY = touch.clientY - 30;
  
    playerDragStart(player, e);
  
    // the 'drag' behavior automatically creates a clone
    // of the element that gets dragged around - we need
    // to mimic that behavior on mobile by cloning it for 
    // dragging
    playerDragClone = player.cloneNode(true);
    playerDragClone.addEventListener("touchend", playerTouchEnd);

    // add the clone to the roster - so it appears
    // we don't want to add it just any shift because the .is_dragging
    // property will affect things
    // but the roster is special because when we drop there - we don't really
    // drop it there. a clone is always placed there.
    //var rosterdiv = document.getElementById("roster");
    //rosterdiv.appendChild(playerDragClone);

    
    // Move the player element with the touch
    window.addEventListener('touchmove', (e) => {
      if (player.getAttribute('isDragging') == "true") {
        e.preventDefault(); // Prevent default touchmove events
        const touch = e.changedTouches[0];
        const x = touch.clientX - offsetX;
        const y = touch.clientY - offsetY;
        
        playerDragClone.style.transform = `translate(${x}px, ${y}px)`;
  
        // for mobile (touch) the hover event doesn't work either
        // so we need to track over to see if it's hovering over the shift
        // blocks and do things here too.
        const droppables = document.querySelectorAll(".shift");
        droppables.forEach((droppable) => {
          if (
            touch.clientX > droppable.getBoundingClientRect().left &&
            touch.clientX < droppable.getBoundingClientRect().right &&
            touch.clientY > droppable.getBoundingClientRect().top &&
            touch.clientY < droppable.getBoundingClientRect().bottom
          ) {
            // The draggable element is dropped inside the droppable area
            dragOverBehavior(droppable, touch.clientY);
          }
        });
  
      }
    });
  } catch (error) {
    window.alert(`An error occurred: ${error.message}`);
  }
}
function playerTouchEnd(e)
{
  var player = this;
  var isDragging = player.getAttribute('isDragging')
  if (isDragging == "true") {
    player.setAttribute("isDragging", "false");
    window.removeEventListener('touchmove', null);
    window.removeEventListener('touchend', null);

    // Reset the player element's position
    player.style.transform = 'translate(0, 0)';
  }
  playerDragEnd(player, e);
}

// need to define the listeners are separate function rather than inline
// because when we clone a node only intrinsic (set in HTML tag) listeners are copied
function playerDragStart(player, e)
{
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

function playerDragEnd(player, e)
{
  player.classList.remove("is-dragging");
  player.style.backgroundColor = player.getAttribute('data-backgroundColor');

  // if it's the roster - clone it so we don't remove it from the roster
  if (player.dataset.fromRoster == "true") {
    const playerClone = player.cloneNode(true);
    // need to add the listeners manually on a cloned node
    // (if not specified instrinicly)
    addListeners(playerClone);

    var rosterdiv = document.getElementById("roster");
    var referenceElement = rosterdiv.children[player.dataset.rosterPosition];
    rosterdiv.insertBefore(playerClone, referenceElement);
  }

  event.preventDefault();
  updateshifts();  
}

// have to create event functions so i can call playerDragStart() 
// from both drag and touch events
function playerDragStartEvent(e)
{
  var player = this;
  playerDragStart(player, e)
}
function playerDragEndEvent(e)
{
  var player = this;
  playerDragEnd(player, e)
}
function addListeners(player)
{
  player.addEventListener("dragstart", playerDragStartEvent);
  player.addEventListener("dragend", playerDragEndEvent);
  player.addEventListener("touchstart", playerTouchStart);
  player.addEventListener("touchend", playerTouchEnd);
}

function dragOverBehavior(droppable, clientY)
{
  const curPlayer = document.querySelector(".is-dragging");

  // you can't drop an identical player
  var shift = droppable;
  const players = shift.querySelectorAll('.player');
  let playerIsDup = false;
  players.forEach((player) => {
    if (player.id == curPlayer.id && player != curPlayer)
    {
      playerIsDup = true;
      return;
    }
  });
  if (playerIsDup == true) {
    return;
  }

  //console.log(curPlayer)
  const bottomPlayer = insertAbovePlayer(droppable, clientY);

  if (!bottomPlayer) {
      droppable.appendChild(curPlayer);
  } else {
      droppable.insertBefore(curPlayer, bottomPlayer);
  }
}

const insertAbovePlayer = (droppable, mouseY) => {
  const els = droppable.querySelectorAll(".player:not(.is-dragging)");

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
    addListeners(player);

    
    // tried 'drop' but you can drag your item into a 
    // list but then mouse our of the list and then the
    // drop event doesn't trigger
    // dragend works better
    //player.addEventListener("drop", (event) => {  
    //});
  });
  
  droppables.forEach((droppable) => {
    droppable.addEventListener("dragover", (e) => {
      e.preventDefault();
      dragOverBehavior(droppable, e.clientY);
    
    });
  });
  

}
