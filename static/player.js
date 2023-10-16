const form = document.getElementById("player-form");
const input = document.getElementById("player-input");
const shift1Lane = document.getElementById("shift1");

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const value = input.value;

  if (!value) return;

  const newPlayer = document.createElement("p");
  newPlayer.classList.add("player");
  newPlayer.setAttribute("draggable", "true");
  newPlayer.innerText = value;

  newPlayer.addEventListener("dragstart", () => {
    newPlayer.classList.add("is-dragging");
  });
 
  newPlayer.addEventListener("dragend", () => {
    newPlayer.classList.remove("is-dragging");
  });

  shift1Lane.appendChild(newPlayer);

  input.value = "";
});
