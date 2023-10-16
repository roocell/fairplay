import random
import os
from logger import log as log
from shift_limits import get_shift_limits, get_max_shifts, verify_shift_limits, get_pcount_for_max_shifts
from utils import no_duplicates
import player
import strong
import argparse
import commentjson
import prevshift

# input
# players.txt  - a list of players
# stronglines.txt - a list of strong 3 player groups
# prevshifts.txt - a list of comma separated values game#,player,minutes
#           - this is a running file of all the minutes played by a player for all games
# output
#   dumps the recommended shifts for the next game

players = []  # an array of Players
stronglines = []  # an array of an array of Players
shifts = []  # an array of an array of Players


def run_fairplay_algo(players, stronglines):
  global shifts
  shifts = get_shifts(players, stronglines)
  print_shifts(shifts)

  if verify_shift_limits(len(players), [p.shifts for p in players]):
    log.debug("VERIFICATION PASSED")

  verify_unique_players_on_shifts(shifts)


def load(players_file, stronglines_file, prevshifts_file):
  with open(players_file, "r") as file:
    file_contents = file.read()
    players_json = commentjson.loads(file_contents)
  with open(stronglines_file, "r") as file:
    file_contents = file.read()
    stronglines_json = commentjson.loads(file_contents)
  with open(prevshifts_file, "r") as file:
    file_contents = file.read()
  prevshifts_json = commentjson.loads(file_contents)

  global players, stronglines
  players = player.load(players_json, prevshifts_json)
  player.dump(players)

  stronglines = strong.load(players, stronglines_json)
  #strong.dump(stronglines)

  # default the shifts to all players in first shift
  shifts.append(players)
  for i in range(7):
    shifts.append([])  # fill in 7 more empty lines


def find_player_in_shift(player_name, shift):
  for p in shift:
    if p.name == player_name:
      return p
  return None


def reset_player_shifts():
  global players
  for p in players:
    p.shifts = 0


# gets called when a player is moved on the web
# data is a list of dictionaries of players (just names for now)
def updateshiftsfromweb(data):
  global shifts, players

  log.debug("updating shifts)")
  log.debug(data)

  shifts = []  # just recreate shifts based on web data
  for webshift in data:
    s = []
    for pw in webshift:
      pwname = pw["name"].strip()
      pp = player.find(players, pwname)
      if pp == None:
        log.error(f"could not find player {pwname}")
      s.append(pp)
    shifts.append(s)

  print_shifts(shifts)


def load_files_and_run(players_file, stronglines_file, prevshifts_file):
  load(players_file, stronglines_file, prevshifts_file)
  global players, stronglines
  run_fairplay_algo(players, stronglines)


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
      if p.shifts < max_shifts:
        if p not in pnm_players:
          pnm_players.append(p)
  return pnm_players


# build a set of groups of strongline players
def get_strongline_shifts(players, stronglines, num_shifts=8):
  # shuffle them so we don't always have the same starting line
  random.shuffle(stronglines)

  shiftlimits = get_shift_limits(len(players))
  pcount_for_max_shifts = get_pcount_for_max_shifts(len(players))
  max_shifts = get_max_shifts(len(players))
  log.debug(shiftlimits)
  log.debug(max_shifts)
  log.debug(pcount_for_max_shifts)

  # make 8 shifts with stronglines
  shifts = []
  for i in range(num_shifts):
    sl = stronglines[i % len(stronglines)]

    # as we do this keep track of shifts
    add_shift = True
    for p in sl:
      # consider shift limits
      pshifts = []
      pshifts = [pp.shifts for pp in players]  # all players shifts
      available_max_shift_spots = pcount_for_max_shifts - pshifts.count(
          max_shifts)

      # stop filling in stronglines if:
      #  - this player is already at max shifts
      #log.debug(f" {p.shifts} < {max_shifts}")
      if p.shifts >= max_shifts:
        add_shift = False

      #  - we already have enough players at max shifts
      #log.debug(f" {pshifts.count(max_shifts)} < {pcount_for_max_shifts}")
      if pshifts.count(max_shifts) >= pcount_for_max_shifts:
        add_shift = False

      #  - will adding this shift put you over?
      #log.debug(f" {available_max_shift_spots} < {len(sl)}")
      if p.shifts == (max_shifts - 1) and available_max_shift_spots < len(sl):
        add_shift = False

    if add_shift:
      # make a copy of the stronglong so we're not putting
      # the same strongline object into multiple shifts
      # this will mess up shift counting otherwise
      for p in sl:
        p.shifts += 1
      shifts.append(sl.copy())
      #log.debug(f"add Shift: {sl[0].name} {sl[0].shifts}")
    else:
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
  assert len(shifts) == num_shifts, "didn't get to the right number of shifts"
  return shifts


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

  for s in shifts:
    while len(s) < 5:  # keep going until the shift is full
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
      p_to_add.shifts += 1
      assert p_to_add.shifts <= max_shifts, "ERROR: we've exceeded max shifts"

      #log.debug(f"ADDING {p_to_add.name}")
      s.append(p_to_add)

      # redo the player sorting so we're always picking a randomized player with
      # the least amount of shifts
      next_players = player.get_sorted(next_players)

  return shifts


def get_shifts(players, stronglines, num_shifts=8):
  shifts = get_strongline_shifts(players, stronglines, num_shifts)
  log.debug("STRONGLINE SHIFTS")
  #print_shifts(shifts)
  shifts = fill_shifts(players, shifts, stronglines)
  return shifts


def verify_unique_players_on_shifts(shifts):
  for s, shift in enumerate(shifts):
    for i, p in enumerate(shift):
      for j, pp in enumerate(shift):
        if i != j:
          assert pp != p, f"ERROR {p.name} is twice on shift {s+1}"
