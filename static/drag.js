
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

  if (player!== null && player.parentNode !== null)
  {
    if (player.parentNode.id !== "roster")
    {
      player.parentNode.removeChild(player);
    }
  }

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


  // make roster a dropable - but it'll act differently and consume the player (like a delete)
  const roster = document.getElementById("roster");
  roster.addEventListener("dragover", (e) => {
    e.preventDefault();
    const curPlayer = document.querySelector(".is-dragging");

    // TODO: apparently the drag image can only be changed on drag start
    // not on dragover on another element.
    // apparently this can't be done due to security reasons?
    // https://stackoverflow.com/questions/48212718/how-to-change-icon-during-dragover-dragenter-html-5-drag-and-drop
    //const dragImage = document.getElementById('delete-icon');
    //e.dataTransfer.setDragImage(dragImage, 0, 0);
    // const dragImage = new Image();
    // dragImage.src = '/static/delete.png';
    // e.dataTransfer.setDragImage(dragImage, 0, 0);

    // add to roster - but hidden - so the object still exists if user
    // drags back to another shift
    var roster = document.getElementById("roster");
    roster.appendChild(curPlayer);
    curPlayer.style.display = none;

    // if it's in the roster at drag end - it will be deleted
  });  
  roster.addEventListener("dragleave", (e) => {
    e.preventDefault();
    const curPlayer = document.querySelector(".is-dragging");
    curPlayer.style.display = blocking;
  });  

}
