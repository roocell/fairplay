import random
import os
from logger import log as log
from shift_limits import get_shift_limits, get_max_shifts, verify_shift_limits, get_pcount_for_max_shifts, assert_shift_limits
from utils import no_duplicates
import player
import strong
import argparse
import commentjson
import double
import models
from sqlalchemy.orm.exc import NoResultFound
from flask_login import current_user
from models import db_get_game, db_get_full_roster, db_get_groups, db_add_player_to_roster, db_remove_player_from_roster, db_set_groups, db_get_groups
from models import Player

def fairplay_validation(players, shifts):
  if verify_shift_limits(players, shifts):
    log.debug("VERIFICATION PASSED")

  verify_unique_players_on_shifts(shifts)
  double.check_consecutive(players, shifts)

def run_fairplay_algo(data):
  log.debug(data)

  shifts, roster = db_get_game(current_user.id, data['game_id'])
  groups = db_get_groups(current_user.id)

  if data != None:
    # only clear the shifts that aren't locked
    shifts = clear_shifts_not_locked(roster, data)

  get_shifts(shifts, roster, groups)
  fairplay_validation(roster, shifts)
  return roster, shifts

# fairplay algorithm updates player shift count (get_shifts())
# but not when a game is loaded - this is to be used in the latter case.
def fairplay_updateshiftcount(shifts, players):
  reset_player_shifts(players)
  for s in shifts:
    for p in s:
      p.shiftcnt += 1

def load_from_file(players_file, stronglines_file):
  with open(players_file, "r") as file:
    file_contents = file.read()
    players_json = commentjson.loads(file_contents)
  with open(stronglines_file, "r") as file:
    file_contents = file.read()
    stronglines_json = commentjson.loads(file_contents)


  players = player.load(players_json)
  player.dump(players)

  stronglines = strong.load(players, stronglines_json)
  return (players, stronglines)


def find_player_in_shift(player_name, shift):
  for p in shift:
    if p.name == player_name:
      return p
  return None


def reset_player_shifts(players):
  for p in players:
    p.shiftcnt = 0


def reset_player_locks(players):
  for p in players:
    p.lts = [0] * 8


def clear_shifts_not_locked(players, data):
  # assume roster isn't changing

  reset_player_shifts(players)
  reset_player_locks(players)

  # recreate the shifts array - but hold onto anything locked
  # if not locked we will fill in an empty shift
  # remember to track player shifts and lockedtoshift
  shifts = []
  shiftsFromClientSide = data["shifts"]
  for i, webshift in enumerate(shiftsFromClientSide):
    s = []
    for pw in webshift:
      pwname = pw["name"].strip()
      pp = player.find(players, pwname)
      if pp == None:
        log.error(f"could not find player {pwname}")
      else:
        # only keep (and update) locked players
        if pw["lts"] == True:
          log.debug(f"locking {pp.name}")
          pp.shiftcnt += 1
          # we may be locking the player to the shift - update the player array
          pp.lts[i] = int(pw["lts"])
          s.append(pp)
    shifts.append(s)
  return shifts


# updates server side view of roster and shifts (from web actions)
# data is array of players names in roster
# and several other arrays of players names for shifts.
# player name is always used to ID player back to server.
# TODO: we could use player number instead of name to make it more efficient
# TODO: should have strong validation here for security
def update(data):

  log.debug("updating server side data")
  log.debug(data)

  # load server side data from database
  shifts, roster = db_get_game(current_user.id, data['game_id'])

  clientSideGroups = data["groups"]
  if len(clientSideGroups) > 0:
    # roster page update
    db_set_groups(current_user.id, clientSideGroups)
  groups = db_get_groups(current_user.id)
  

  reset_player_shifts(roster)
  reset_player_locks(roster)

  # reset server data
  serverSideRoster = roster.copy()
  roster = []  # new roster
  shifts = []

  # how to also calculate player things that the fairplay algorithm figures out
  # like shifts

  #player.dump(serverSideRoster)

  rosterFromClientSide = data["roster"]
  shiftsFromClientSide = data["shifts"]

  rosterpage = False
  if len(shiftsFromClientSide) == 0:
    rosterpage = True

  # update roster
  # 2 cases
  # 1. removing roster player from mainpage
  # 2. adding new player from roster page
  for clientSidePlayer in rosterFromClientSide:
    p = player.find(serverSideRoster, clientSidePlayer["name"])
    if p == None:
      # this could be an update from the roster page, adding new players
      # let's just assume this.
      # just update roster with new player
      log.debug(f"adding new player: {clientSidePlayer['number']} {clientSidePlayer['name']}")

      # update persistant copy (do this first so we know db id)
      dbid = db_add_player_to_roster(current_user.id, clientSidePlayer['name'], clientSidePlayer["number"])
      p = player.Player(clientSidePlayer["name"], clientSidePlayer["number"], dbid)


    # update non-persistant copy
    roster.append(p)

  # check for deleted players
  # only do this for roster page 
  if len(shiftsFromClientSide) == 0:
      # if there are no shifts, then it's the roster page.
      # fine for now - but should be something more explicit.
      for serverSidePlayer in serverSideRoster:
        p = player.find(roster, serverSidePlayer.name)
        if p == None:
          log.debug(f"removing player {serverSidePlayer.name} {serverSidePlayer.number}")
          db_remove_player_from_roster(current_user.id, serverSidePlayer.name, serverSidePlayer.number)


  #log.debug("New roster")
  #player.dump(players)

  # fixup stronglines (players could be removed from roster)
  stronglines = groups
  stronglines = strong.reload(roster, stronglines)
  #strong.dump(stronglines)

  for i, webshift in enumerate(shiftsFromClientSide):
    s = []
    log.debug(webshift)
    for pw in webshift:
      pwname = pw["name"].strip()
      pp = player.find(roster, pwname)
      if pp == None:
        log.error(f"could not find player {pwname}")
      else:
        pp.shiftcnt += 1
        # we may be locking the player to the shift
        # (but moved a player that triggered an update - for example)
        # - update the player array
        pp.lts[i] = int(pw["lts"])
        s.append(pp)
    shifts.append(s)

  double.check_consecutive(roster, shifts)
  #print_shifts(shifts)
  return (roster, shifts, groups)


def load_files_and_run(players_file, stronglines_file):
  # TODO: load from file and put into db 
  players, stronglines = load_from_file(players_file, stronglines_file)
  players, shifts = run_fairplay_algo(None)
  assert_shift_limits(players, shifts)


def print_shifts(shifts):
  for i, s in enumerate(shifts, start=1):
    log.debug(" ")
    log.debug(f"shift {i}")
    player.dump(s)


def get_players_not_at_max_shifts(players, shifts):
  pnm_players = []
  max_shifts = get_max_shifts(len(players))
  for s in shifts:
    for p in s:
      if p.shiftcnt < max_shifts:
        if p not in pnm_players:
          pnm_players.append(p)
  return pnm_players


# build a set of groups of strongline players
# this is how we start building our shifts
def get_strongline_shifts(shifts, players, stronglines, num_shifts=8):
  # if there's no stronglines defined - do nothing
  if len(stronglines) == 0:
    return
  
  # shuffle them so we don't always have the same starting line
  random.shuffle(stronglines)

  shiftlimits = get_shift_limits(len(players))
  pcount_for_max_shifts = get_pcount_for_max_shifts(len(players))
  max_shifts = get_max_shifts(len(players))
  log.debug(shiftlimits)
  log.debug(max_shifts)
  log.debug(pcount_for_max_shifts)

  # make 8 shifts with stronglines
  for i in range(num_shifts):
    sl = stronglines[i % len(stronglines)]

    # as we do this keep track of shifts
    add_shift = True
    for p in sl:
      # consider shift limits
      pshifts = []
      pshifts = [pp.shiftcnt for pp in players]  # all players shifts
      available_max_shift_spots = pcount_for_max_shifts - pshifts.count(
          max_shifts)

      # stop filling in stronglines if:
      #  - this player is already at max shifts
      #log.debug(f" {p.shiftcnt} < {max_shifts}")
      if p.shiftcnt >= max_shifts:
        add_shift = False

      #  - we already have enough players at max shifts
      #log.debug(f" {pshifts.count(max_shifts)} < {pcount_for_max_shifts}")
      if pshifts.count(max_shifts) >= pcount_for_max_shifts:
        add_shift = False

      #  - will adding this shift put you over?
      #log.debug(f" {available_max_shift_spots} < {len(sl)}")
      if p.shiftcnt == (max_shifts - 1) and available_max_shift_spots < len(sl):
        add_shift = False


    # if the shift isn't empty - don't insert the strongline
    # this will also cover the case where a shift is locked
    if len(shifts[i]) > 0:  # must be locked
      add_shift = False

    if add_shift:
      # make a copy of the stronglong so we're not putting
      # the same strongline object into multiple shifts
      # this will mess up shift counting otherwise
      for p in sl:
        p.shiftcnt += 1
      shifts[i] = sl.copy()
      #log.debug(f"add Shift: {sl[0].name} {sl[0].shiftcnt}")
    else:
      if len(sl) > 0: # could be no stronglines defined
        log.debug(f"SHIFT LIMIT REACHED: {sl[0].name}")

  # now the shifts are filled with stronglines
  # all shifts could be filled - but they could also be partly filled
  # if there wasn't enough stronglines defined
  # if that's the case we should go through and create num_shifts shifts
  # and space out the stronglines
  if len(shifts) < num_shifts:
    diff = num_shifts - len(shifts)
    for i in range(diff):
      shifts.insert((i + 1) * diff, [])

  # verify we have the proper amount of shifts
  assert len(
      shifts
  ) == num_shifts, f"didn't get to the right number of shifts {len(shifts)}"


def fill_shifts(players, shifts, stronglines):
  # assumes shifts is already an 8 shift array partially filled in with players

  # get a list of players not in the stronglines
  nsl_players = strong.get_players_not_in_stronglines(players, stronglines)
  assert no_duplicates(nsl_players), "nsl_players has duplicates"
  #log.debug("nsl_players")
  #player.dump(nsl_players)
  # get a list of players in the shifts that haven't reached the max shifts
  pnm_players = get_players_not_at_max_shifts(players, shifts)
  assert no_duplicates(pnm_players), "pnm_players has duplicates"
  #log.debug("pnm_players")
  #player.dump(pnm_players)

  # combine them sort them by shifts and randomize within the groups
  next_players = player.get_sorted(nsl_players + pnm_players)

  max_shifts = get_max_shifts(len(players))

  for i, s in enumerate(shifts, start=1):
  #for s in shifts:
    while len(s) < 5 and len(s) < len(next_players):  # keep going until the shift is full
      #log.debug("next_players")
      #player.dump(next_players)

      # sometimes a player will bubble to the top and could
      # be inserted into the same line twice
      # avoid this by looping through next player list
      n = 0
      p_to_add = next_players[n]
      while p_to_add in s:
        p_to_add = next_players[n]
        n = n + 1

      # fill in the shift and increment shifts
      # but also keep on eye on max shifts to make sure there's no error
      p_to_add.shiftcnt += 1
      assert p_to_add.shiftcnt <= max_shifts, f"ERROR: we've exceeded max shifts {max_shifts} for {len(players)}"

      #log.debug(f"ADDING {p_to_add.name} to shift {i}")
      s.append(p_to_add)

      # redo the player sorting so we're always picking a randomized player with
      # the least amount of shifts
      next_players = player.get_sorted(next_players)

  return shifts


def get_shifts(shifts, players, stronglines, num_shifts=8):
  get_strongline_shifts(shifts, players, stronglines, num_shifts)
  fill_shifts(players, shifts, stronglines)


def verify_unique_players_on_shifts(shifts):
  for s, shift in enumerate(shifts):
    for i, p in enumerate(shift):
      for j, pp in enumerate(shift):
        if i != j:
          assert pp != p, f"ERROR {p.name} is twice on shift {s+1}"
