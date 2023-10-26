function getdomdata()
{
  var data = {
    shifts: [],
    roster: []
  };
  
  var roster = document.getElementById("roster");
  var players = roster.querySelectorAll(".player");
  players.forEach((player) => {
    data.roster.push({
      "name" : player.id
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
            "name" : player.id
              })
        });
    data.shifts.push(parray)
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
        updateDom(data);
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });

}

function updateDomRoster(data)
{
  var lanes = document.getElementById("lanes");
  lanes.innerHTML = "";
 
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
    playerp.id = player.name;
    playerp.innerHTML = player.number + " " + player.name + " " + player.shifts;
    playerp.setAttribute('data-backgroundColor', player.colour);
    rosterdiv.appendChild(playerp);
  });
  lanes.appendChild(rosterdiv);
}

function updateDom(data)
{
  console.log("updating DOM:");
  console.log(data);

  // update the DOM with the new shifts
  var lanes = document.getElementById("lanes");

  updateDomRoster(data);

  // put a div around the shifts so we can do 2 rows of 4
  var shiftscontainer = document.createElement('div');
  shiftscontainer.id = "shiftscontainer";
  shiftscontainer.className = "shiftscontainer";

  var shiftsrow1 = document.createElement('div');
  shiftsrow1.id = "shiftsrow";
  shiftsrow1.className = "shiftsrow";

  var shiftsrow2 = document.createElement('div');
  shiftsrow2.id = "shiftsrow";
  shiftsrow2.className = "shiftsrow";

  shiftscontainer.appendChild(shiftsrow1);
  shiftscontainer.appendChild(shiftsrow2);

  lanes.appendChild(shiftscontainer);

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
      playerp.setAttribute('data-violates', player.violates);

      shiftdiv.appendChild(playerp);
    });
    if (i >=1 && i <= 4)
    {
      shiftsrow1.appendChild(shiftdiv);
    } else {
      shiftsrow2.appendChild(shiftdiv);
    }
  });
  setupDraggablesAndDroppables();
}

function getserverdata()
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
        updateDom(data);
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });
}

function getserverdata_roster()
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
        updateDomRoster(data);
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
        updateDom(data);
    }).catch(error => {
        // Handle any network or request-related errors here
        console.error(error);
    });
}
