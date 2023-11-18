const form = document.getElementById("player-form");
const player_number = document.getElementById("player-number");
const player_name = document.getElementById("player-name");

form.addEventListener("submit", (e) => {
  e.preventDefault();
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
  newPlayer.id = name;
  newPlayer.dataset.number = number;
  newPlayer.dataset.name = name;

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
});
