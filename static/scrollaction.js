/* scroll behavior on mobile (touch) when dragging players */

var thresholdPercentageHorz = 0.10;
var thresholdPercentageVert = 0.10;
var scrollStepSize = 10;
var scrollTimerDelay = 10;
var screenScrollHorzTimerId = null;
var screenScrollVertTimerId = null;
function startScreenScrollHorz(direction) {
  if (screenScrollHorzTimerId != null)
  {
    return;
  }
  screenScrollHorzTimerId = setInterval(function() {
    var lanes = document.getElementById("lanes");
    lanes.scrollLeft += scrollStepSize*direction;
  }, scrollTimerDelay); // ms
}
function stopScreenScrollHorz() {
  clearInterval(screenScrollHorzTimerId);
  screenScrollHorzTimerId = null;
}

let doneScrolling = true;
function startScreenScrollVert(direction) {

  if (doneScrolling == false)
  {
    return;
  }
  doneScrolling = false;
  console.log(Date.now() + "scrolling");
  //this kind of works
   window.scrollTo({
     top: document.documentElement.scrollTop + 200*direction,
     behavior: 'smooth' // for smooth scrolling, 'auto' for instant scrolling
  });
  
  screenScrollVertTimerId = setInterval(function() {
    try {
      // this works but is janky
      //document.documentElement.style.transition = 'scrollTop 0.5s ease-in-out';
     // document.documentElement.scrollTop += scrollStepSize*direction;

      // this does not scroll at all.
      // var lanes = document.getElementById("lanes");
      // lanes.scrollTo(lanes.scrollY, lanes.scrollY+scrollStepSize*direction); 
      } catch (error) {
        window.alert(`An error occurred: ${error.message}`);
      }
      doneScrolling = true;
  }, 500); // ms
}
function stopScreenScrollVert() {
  clearInterval(screenScrollVertTimerId);
  screenScrollVertTimerId = null;
}

function stopAllScreenScroll()
{
  stopScreenScrollVert();
  stopScreenScrollHorz();
}

function isTouchRight(touch)
{
  var touchX = touch.clientX;
  var screenWidth = window.innerWidth;
  var threshold = screenWidth - screenWidth*thresholdPercentageHorz;
  if (touchX > threshold) {
    return true;
  }
  return false;
}
function isTouchLeft(touch)
{
  var touchX = touch.clientX;
  var screenWidth = window.innerWidth;
  var threshold = screenWidth*thresholdPercentageHorz;
  if (touchX < threshold) {
    return true;
  }
  return false;
}

function isTouchTop(touch)
{
  var touchY = touch.clientY;
  var screenHeight = window.innerHeight;
  var threshold = screenHeight*thresholdPercentageVert;
  if (touchY < threshold) {
    return true;
  }
  return false;
}

function isTouchBottom(touch)
{
  var touchY = touch.clientY;
  var screenHeight = window.innerHeight;
  var threshold = screenHeight*(1-thresholdPercentageVert);
  if (touchY > threshold) {
    return true;
  }
  return false;
}

function processScrollAction(touch)
{
  if (isTouchRight(touch))
  {
    startScreenScrollHorz(1);
  } else if (isTouchLeft(touch)) {
      startScreenScrollHorz(-1);
  } else {
    stopScreenScrollHorz();
  }
  if (isTouchTop(touch))
  {
    startScreenScrollVert(-1);
  } else if (isTouchBottom(touch)) {
    startScreenScrollVert(1);
  } else {
    stopScreenScrollVert();
  }
}