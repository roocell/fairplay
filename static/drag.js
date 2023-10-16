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
      // Handle the response from the server
  });
}

const draggables = document.querySelectorAll(".player");
const droppables = document.querySelectorAll(".shift");

draggables.forEach((player) => {
  player.addEventListener("dragstart", () => {
    player.classList.add("is-dragging");
  });
  player.addEventListener("dragend", (event) => {
    player.classList.remove("is-dragging");
    event.preventDefault();
    updateshifts();  
  });
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

    const bottomPlayer = insertAbovePlayer(zone, e.clientY);
    const curPlayer = document.querySelector(".is-dragging");

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
