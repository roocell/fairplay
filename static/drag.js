const draggables = document.querySelectorAll(".player");
const droppables = document.querySelectorAll(".shift");

draggables.forEach((player) => {
  player.addEventListener("dragstart", () => {
    player.classList.add("is-dragging");
  });
  player.addEventListener("dragend", () => {
    player.classList.remove("is-dragging");
  });
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
