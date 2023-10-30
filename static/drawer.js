function updateDomWithDrawer()
{
  console.log("updateDomWithDrawer");
  // add the open drawer button to the board
  const board = document.querySelector('.board');
  
  //<button class="open-button" onclick="openDrawer()">></button>
  const drawerButton = document.createElement('button');
  drawerButton.className = 'drawer-button';
  drawerButton.textContent = '>'; // Set the button text
  drawerButton.onclick = openDrawer; // Set the click event listener
  board.appendChild(drawerButton);

  // move the shifts to the right a bit
  const lanes = document.getElementById('lanes');
  // shift is 225px wide
  const pos = window.innerWidth / 2 - 225 / 2 + 20;
  lanes.style.paddingLeft = `${pos}px`;
}


function openDrawer() {
  const drawer = document.querySelector('.drawer');
  drawer.style.left = '0';
  const drawerButton = document.querySelector('.drawer-button');
  drawerButton.onclick = closeDrawer;
  drawerButton.innerHTML = "<";

  // when the drawer open - move the shifts over
  // TODO: this doens't work probably due to other styles
  // const halfScreenWidth = window.innerWidth / 2;
  // const lanes = document.querySelector('.lanes');
  // //lanes.style.left = `${halfScreenWidth}px`;
  // lanes.style.left = '200px';
}

function closeDrawer() {
  const drawer = document.querySelector('.drawer');
  drawer.style.left = '-250px'; /* Return it off-screen to the left */
  const drawerButton = document.querySelector('.drawer-button');
  drawerButton.onclick = openDrawer;
  drawerButton.innerHTML = ">";

  // const lanes = document.querySelector('.lanes');
  // lanes.style.left = '0px';
}