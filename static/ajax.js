// use chrome devtools to test
const isMobile = /iPhone|iPad|iPod|Android|Windows Phone/.test(navigator.userAgent);

function onLoadMain()
{
  getgames(0)
    .then(()=> {
      getserverdata(game_id=document.getElementById("games").options[0].value); // default
    })
      .catch(error => {
        // Handle errors here
        console.error(error);
    });

  setupDraggablesAndDroppables();

  if (isMobile)
  {
    updateDomWithDrawer();
  }
}

function onLoadRoster()
{
  getserverdata_roster();
  // now that there's groups we need roster in a drawer here too
  if (isMobile)
  {
    updateDomWithDrawer();
  }
  
}

// TODO: this is brute force - need some better server side implementation
// with Celery / evenlet
function showLoadingOverlay() {
  var loadingOverlay = document.getElementById('loading-overlay');
  loadingOverlay.style.display = 'flex';
}

function hideLoadingOverlay() {
  var loadingOverlay = document.getElementById('loading-overlay');
  loadingOverlay.style.display = 'none';
}

function getdomdata()
{
  var selectElement = document.getElementById("games");

  var data = {
    game_id : (selectElement) ? selectElement.value : 0, // could be roster page - make 0
    shifts: [],
    groups: [],
    roster: []
  };
  
  var roster = document.getElementById("roster");
  var players = roster.querySelectorAll(".player");
  players.forEach((player) => {
    data.roster.push({
      "id" : player.id,
      "name" : player.name,
      "number" : player.number,
    })
  });
  
  // build data of the shifts on screen
  // to send back to python
  var shifts = document.querySelectorAll(".shift");
  shifts.forEach(function(shift) {
    // inside each shift is a player class
    var parray = new Array();
    var players = shift.querySelectorAll(".player");
        players.forEach(function(player) {
          parray.push({
            "name" : player.name,
            "lts" : shift.classList.contains("locked-outline")
              })
        });
    data.shifts.push(parray)
  });

  var groups = document.querySelectorAll(".group");
  groups.forEach(function(group) {
    // inside each shift is a player class
    var parray = new Array();
    var players = group.querySelectorAll(".player");
        players.forEach(function(player) {
          parray.push({
            "name" : player.name,
          })
        });
    data.groups.push(parray)
  });

  return data;
}

// sends data back to server to update
// roster and shifts
function updatedata()
{
  var data = getdomdata();
  var datastr = JSON.stringify(data);
  console.log("datastr:" + datastr);
  //console.log(JSON.stringify(data));
  // Make a POST request to your Flask route with the JSON data
  showLoadingOverlay();
  fetch('/updatedata', {
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
        // Handle the JSON data received from the server
        updateDom(window.location.href.includes("settings") ? false : true, data);
        hideLoadingOverlay();
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
        hideLoadingOverlay();
    });

}

// populates the DOM with the roster
// used on both the main page and the roster page
function updateDomRoster(mainpage, data)
{
  // update the roster in the DOM with the players again
  var rosterdiv = document.createElement('div');
  rosterdiv.className = "roster";
  rosterdiv.id = "roster";
  var rheader = document.createElement('h3');
  rheader.className = "heading";
  rheader.innerHTML = "Roster";
  rosterdiv.appendChild(rheader);

  // trash can
  var trashcan = document.createElement("p");
  trashcan.style.textAlign = "center";
  trashcan.classList.add("trashcan");
  trashcan.id = "trashcan";
  var img = document.createElement("img");
  img.src = "/static/trashcan.png";
  img.alt = "remove player from roster";
  img.width = 50;
  trashcan.appendChild(img);

  rosterdiv.appendChild(trashcan);

  var playersData = JSON.parse(data.players);
  playersData.forEach(function(player) {
    var playerp = document.createElement("p");
    playerp.classList.add("player");
    playerp.setAttribute("draggable", "true");
    playerp.setAttribute("isDragging", "false");
    playerp.id = player.id;
    playerp.name = player.name;
    playerp.number = player.number;
    playerp.innerHTML = player.name;
    playerp.setAttribute('data-backgroundColor', player.colour);
    playerp.setAttribute('number-decoration', player.number);
    if (mainpage && player.shiftcnt > 0)
    {
      playerp.setAttribute('shifts-decoration', player.shiftcnt);
    } else {
      playerp.classList.add('hide-decoration');
    }
    rosterdiv.appendChild(playerp);
  });
 
  if (isMobile == false) {
    var lanes = document.getElementById("lanes");
    lanes.appendChild(rosterdiv);
  }
  // for mobile put the roster into a drawer
  else {
    var drawer = document.getElementById("drawer");
    drawer.innerHTML = "";
    drawer.appendChild(rosterdiv);
  }
}

function shortenName(name) {
  const parts = name.split(' ');
  if (parts.length > 1) {
    // Take the first letter of each part
    const shortened = parts.map(part => part.slice(0, 2)).join('');
    return shortened;
  } else {
    // If there is only one part, take the first three letters
    return name.substring(0, 3);
  }
}

function displayShiftAsLocked(shift, lockimg)
{
  lockimg.src = "/static/lock.png";
  shift.classList.add("locked-outline");
}

function handleLockClick(lockimg)
{
  var shift = lockimg.parentElement;
  if (shift.classList.contains("locked-outline"))
  {
    lockimg.src = "/static/unlock.png";
    shift.classList.remove("locked-outline");
  } else {
    displayShiftAsLocked(shift, lockimg);
  }
  
}

function capitalizeFirstLetter(inputString) {
  return inputString[0].toUpperCase() + inputString.slice(1);
}

function updateDomShifts(mainpage, data)
{
  // on the mainpage we display the shifts
  // on the roster page we display the groups
  if (mainpage)
  {
    prefix = "shift"
    shiftdata = data.shifts;
  } else {
    prefix = "group"
    shiftdata = data.groups;

  }

  // groups will reuse the shifts class for CSS

  // put a div around the shifts so we can do 2 rows of 4
  var shiftscontainer = document.createElement('div');
  shiftscontainer.id = prefix + "s" + "container";
  shiftscontainer.className = prefix + "s" + "container";

  var shiftsrow1 = document.createElement('div');
  var shiftsrow2 = document.createElement('div');
  shiftsrow1.id = shiftsrow2.id = prefix + "s" + "row";
  shiftsrow1.className = shiftsrow2.className = prefix + "s" + "row"; // TODO: there's no groupsrow class (but ok?)

  shiftscontainer.appendChild(shiftsrow1);
  shiftscontainer.appendChild(shiftsrow2);

  lanes.appendChild(shiftscontainer);
  if (!mainpage)
  {
    generateSettingsDiv(shiftscontainer);
  }

  var i = 0;
  var shiftsData = JSON.parse(shiftdata);
  shiftsData.forEach(function(shift) {
    i++;
    var shiftdiv = document.createElement('div');
    shiftdiv.className = prefix;
    shiftdiv.id = prefix + i;

    // add lock button to shiftdiv
    var lockimg = document.createElement('img');
    lockimg.className = "lock-button";
    lockimg.src = "/static/unlock.png";
    lockimg.alt = "lock";
    lockimg.onclick = function() {
      handleLockClick(lockimg);
    };

    if (mainpage)
    {
      //<a href="https://www.flaticon.com/free-icons/lock" title="lock icons">Lock icons created by Dave Gandy - Flaticon</a>
      shiftdiv.appendChild(lockimg);
    }
    
    var header = document.createElement('h3');
    header.className = "heading";
    header.style.textAlign = "right";
    header.innerHTML = capitalizeFirstLetter(prefix) + i;
    shiftdiv.appendChild(header);
   
    shift.forEach(function(player) {
      var playerp = document.createElement('p');
      playerp.className = "player";
      playerp.draggable = "true";
      playerp.id = player.id;
      playerp.name = player.name;
      playerp.number = player.number;
      if (isMobile)
      {
        // in case we want a different display for mobile
        //playerp.innerHTML = player.number + " " + shortenName(player.name) + " " + player.shiftcnt;
        playerp.innerHTML = player.name;
      } else {
        playerp.innerHTML = player.name;
      }
      playerp.setAttribute('data-backgroundColor', player.colour);
      playerp.setAttribute('data-dbl', player.dbl[i-1]);
      playerp.setAttribute('data-violates', player.violates);
      playerp.setAttribute('number-decoration', player.number);
      if (mainpage)
      {
        playerp.setAttribute('shifts-decoration', player.shiftcnt);
      } else {
        playerp.classList.add('hide-decoration');
      }

      shiftdiv.appendChild(playerp);

      // if any player was locked - lock the shift
      // doesn't kill us to do it multiple times
      if (player.lts[i-1] == 1)
      {
        // assume the log img is the first img in the shiftdiv
        lockimg = shiftdiv.getElementsByTagName("img")[0]
        displayShiftAsLocked(shiftdiv, lockimg);
      }
    });

    if (i >=1 && i <= 4)
    {
      shiftsrow1.appendChild(shiftdiv);
    } else {
      shiftsrow2.appendChild(shiftdiv);
    }
  });
}

// used for both the main page and the roster page
// roster page uses shift divs for 'groups'(groups)
function updateDom(mainpage, data)
{
  if (mainpage == true)
  {
    console.log("updating DOM main:");
  } else {
    console.log("updating DOM roster:");
  }

  console.log(data);

  // always clear the lanes div - so it can be repopulated with shifts
  // update the DOM with the new shifts
  var lanes = document.getElementById("lanes");
  lanes.innerHTML = "";
  
  updateDomRoster(mainpage, data);
  updateDomShifts(mainpage, data);
  setupDraggablesAndDroppables();
}


async function getserverdata(game_id)
{
  showLoadingOverlay();
  var data = {"game_id" : game_id};
  var datastr = JSON.stringify(data);
  fetch('/getdata', {
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
        // Handle the JSON data received from the server
        if (data.status == "ok")
        {
          updateDom(true, data);
        } else {
          console.log(data)
        }
        hideLoadingOverlay();
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
        hideLoadingOverlay();
    });
}

function getserverdata_roster()
{
  fetch('/getdataroster', {
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
        updateDom(false, data);
        getSettingsFromServer();
      }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });
}


function runfairplay()
{
  var data = getdomdata();
  var datastr = JSON.stringify(data);

  showLoadingOverlay();
  fetch('/runfairplay', {
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
        // Handle the JSON data received from the server
        updateDom(true, data);
        hideLoadingOverlay();
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
        hideLoadingOverlay();
    });
}
