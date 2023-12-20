
function ifTouchInDroppable(touch, droppable)
{
  if (
    touch.clientX > droppable.getBoundingClientRect().left &&
    touch.clientX < droppable.getBoundingClientRect().right &&
    touch.clientY > droppable.getBoundingClientRect().top &&
    touch.clientY < droppable.getBoundingClientRect().bottom
  ) {
    return true;
  }
  return false;
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
    const offsetX = touch.clientX - 0;
    const offsetY = touch.clientY - 0;
  
    playerDragStart(player, e);
  
    // the 'drag' behavior automatically creates a clone
    // of the element that gets dragged around - we need
    // to mimic that behavior on mobile by cloning it for 
    // dragging
    // clone it after playerDragStart() so it has that dragging style
    //playerDragClone = player.cloneNode(true);
    //playerDragClone.addEventListener("touchend", playerTouchEnd);
    //playerDragClone.style.display = "none";
    
    // add the clone to the roster - so it appears
    // we don't want to add it just any shift because the .is_dragging
    // property will affect things
    // but the roster is special because when we drop there - we don't really
    // drop it there. a clone is always placed there.
    //player.parentNode.insertBefore(playerDragClone, player);
    
    // Move the player element with the touch
    window.addEventListener('touchmove', (e) => {
      try {
        if (player.getAttribute('isDragging') == "true") {
        e.preventDefault(); // Prevent default touchmove events
        const touch = e.changedTouches[0];
        const x = touch.clientX - offsetX;
        const y = touch.clientY - offsetY;
        
        //playerDragClone.style.transform = `translate(${x}px, ${y}px)`;
  
        // for mobile (touch) the hover event doesn't work either
        // so we need to track over to see if it's hovering over the shift
        // blocks and do things here too.
        const droppables = [...document.querySelectorAll(".shift"), ...document.querySelectorAll(".group")];
        droppables.forEach((droppable) => {
          if (ifTouchInDroppable(touch, droppable))
          {
            // The draggable element is dropped inside the droppable area
            dragOverBehavior(droppable, touch.clientY);
          }
        });
        
        // also need to consider the roster droppable
        var roster = document.getElementById("roster");
        if (ifTouchInDroppable(touch, roster))
        {
          rosterDragOverBehavior(roster, touch.clientY);
        }// else if (playerDragClone.dataset.droppingIntoRoster) {
        //}

        // test for drag over trashcan
        const trashcan = document.getElementById("trashcan");
          const curPlayer = document.querySelector(".is-dragging");
        if (ifTouchInDroppable(touch, trashcan))
        {
          trashDragOverBehavior(e);
        } else if (curPlayer.dataset.droppingIntoTrash == "true") {
           trashDragLeaveBehavior(e);
        }

        processScrollAction(touch);

      }
    // every function needs this if you want to catch JS errors on ios
    } catch (error) {
      window.alert(`An error occurred: ${error.message}`);
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
  stopAllScreenScroll();
}

function applyRosterPlayer(player)
{
  player.dataset.fromRoster = true;
  // find index of child in parent - so we can clone in same position
  for (var i = 0; i < player.parentElement.children.length; i++) {
    if (player.parentElement.children[i] == player) {
      player.dataset.rosterPosition = i;
      break;
    }
  }
}

// need to define the listeners are separate function rather than inline
// because when we clone a node only intrinsic (set in HTML tag) listeners are copied
function playerDragStart(player, e)
{
  if (player.parentElement.id == "roster") {
    applyRosterPlayer(player);
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
  var droppingIntoRoster = false;

  var rosterdiv = document.getElementById("roster");
  const trashcan = document.getElementById("trashcan");

  // check for trash
  // NOTE: dataset is treated as a string.
  if (player.dataset.droppingIntoTrash == "true")
  {
    console.log("trashing player");
    player.parentNode.removeChild(player);
    e.preventDefault();
    updatedata(); 
    return;
  } else if (player.parentNode == rosterdiv) {
    droppingIntoRoster = true;
  }  
  
  // if it's the roster - clone it so we don't remove it from the roster
  // we don't do this on touch events (before there we've cloned a drag object instead)
  if (!droppingIntoRoster && player.dataset.fromRoster == "true") {
    console.log("cloning into roster");
    const playerClone = player.cloneNode(true);
    // need to add the listeners manually on a cloned node
    // (if not specified instrinicly)
    addListeners(playerClone);
    playerClone.name = player.name; // these attribs also dont clone
    playerClone.number = player.number;

    var referenceElement = rosterdiv.children[player.dataset.rosterPosition];
    rosterdiv.insertBefore(playerClone, referenceElement);
  }

  e.preventDefault();
  updatedata();
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

  // if we're in the roster - it's now a roster player
  // this addresses a bug with disappearing players
  // shift->roster->shift.
  if (droppable.id == "roster") {
    applyRosterPlayer(curPlayer);
  }
}

function rosterDragOverBehavior(roster, clientY)
{
  try {
    const curPlayer = document.querySelector(".is-dragging");
  
    // remove the cloned player from the roster
    // so it looks like we're putting it back
    const players = roster.querySelectorAll('.player');
      players.forEach((player) => {
      if (player.id == curPlayer.id && player != curPlayer)
      {
        roster.removeChild(player);
      }
    });
    dragOverBehavior(roster,  clientY);
  } catch (error) {
    window.alert(`An error occurred: ${error.message}`);
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

function trashDragOverBehavior(e)
{
  // make smaller, add to trashcan (we need this on playerDragEnd() )
  const curPlayer = document.querySelector(".is-dragging");
  curPlayer.style.transform = "scale(" + 0.5 + ")";
  curPlayer.dataset.droppingIntoTrash = true;
  if (typeof e.dataTransfer !== "undefined")
  {
    e.dataTransfer.dropEffect = "move";
  }
  // can't append a <p> to another <p>
  // so can't put this player into the trash <p>
}
function trashDragLeaveBehavior(e)
{
  // return to normal
  const curPlayer = document.querySelector(".is-dragging");
  curPlayer.style.transform = "scale(" + 1.0 + ")";
  curPlayer.dataset.droppingIntoTrash = false;
  if (typeof e.dataTransfer !== "undefined")
  {
    e.dataTransfer.dropEffect = "copy";
  }
}

function setupDraggablesAndDroppables()
{
  const draggables = document.querySelectorAll(".player");
  const droppables = [...document.querySelectorAll(".shift"), ...document.querySelectorAll(".group")];
 
  draggables.forEach((player) => {
    player.style.backgroundColor = player.getAttribute('data-backgroundColor');
    if ( player.getAttribute('data-dbl') == 1)
    {
      player.classList.add("is-dbl");
    } else {
      player.classList.remove("is-dbl");
    }
    if ( player.getAttribute('data-violates') == 1)
    {
      player.classList.add("is-violates");
    } else {
      player.classList.remove("is-violates");
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
  if (roster != null) // an inital load roster isn't there yet. not until we retrieve the data.
  {
    roster.addEventListener("dragover", (e) => {
      if (e.touches != undefined)
      {
        alert("ERROR: dragover on touch. not expecting this to happen");
      }
      
      e.preventDefault();
      rosterDragOverBehavior(roster, e.clientY);

      // TODO: apparently the drag image can only be changed on drag start
      // not on dragover on another element.
      // apparently this can't be done due to security reasons?
      // https://stackoverflow.com/questions/48212718/how-to-change-icon-during-dragover-dragenter-html-5-drag-and-drop
      //const dragImage = document.getElementById('delete-icon');
      //e.dataTransfer.setDragImage(dragImage, 0, 0);
      // const dragImage = new Image();
      // dragImage.src = '/static/delete.png';
      // e.dataTransfer.setDragImage(dragImage, 0, 0);
 
    });  
    roster.addEventListener("dragleave", (e) => {
      e.preventDefault();

    });  
  }

  // make the roster trashcan a droppable
  // when players are dropped here they get removed from the roster
  // we can do this by simplying adding it to the trashcan and then hiding it
  const trashcan = document.getElementById("trashcan");
  if (trashcan != null)
  {
    trashcan.addEventListener("dragover", (e) => {
      e.preventDefault();
      trashDragOverBehavior(e);
    });
    trashcan.addEventListener("dragleave", (e) => {
      e.preventDefault();
      trashDragLeaveBehavior(e);
    });
  }
}
