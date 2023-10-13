import random
import os
from logger import log as log
from shift_limits import get_shift_limits, get_max_shifts, verify_shift_limits
from utils import no_duplicates

# input
# players.txt  - a list of players
# games.txt - a list of comma separated values game#,player,minutes
#           - this is a running file of all the minutes played by a player for all games
# output
#   dumps the recommended shifts for the next game
#   games_out.txt - adjusted games file that can be used for the next time

roster_file = "roster.out"
players_file = "players.txt"

stronglines_enabled = False
stronglines_file = "stronglines.txt"

prevshift_enabled = False
prevshifts_file = "prevshifts.txt"

# PLAYERS
##################################################


class Player:

  def __init__(self, name, number):
    self.name = name
    self.number = number
    self.shifts = 0


def load_players():
  players = []

  # will load the input data
  with open(players_file, "r") as f:
    for l in f:
      # skip comments or blank lines
      if l.count('#') > 0 or len(l.strip()) <= 0:
        continue
      parts = l.strip().split(',')
      name = parts[1].strip()
      number = parts[0].strip()
      players.append(Player(name, number))
  return players


def find_player(players, name):
  for player in players:
    if player.name == name:
      return player
  return None


def print_players(players):
  for p in players:
    log.debug(f"{p.number} {p.name}: {p.shifts}")


def get_players_sorted(players):
  # sort the players by minutes but shuffle within each group of minutes

  # Sort players by minutes in ascending order
  players.sort(key=lambda x: x.minutes)

  # Create a list of lists to store players grouped by minutes
  groups = []

  current_group = []
  current_minutes = None

  # Iterate through the sorted players and group them
  for player in players:
    if player.minutes != current_minutes:
      if current_group:
        groups.append(current_group)
      current_group = [player]
      current_minutes = player.minutes
    else:
      current_group.append(player)

  # Append the last group
  if current_group:
    groups.append(current_group)

  # go through groups and shuffle each group
  for g in groups:
    random.shuffle(g)

  # now put them all into a flat array again
  resorted_players = []
  for g in groups:
    for p in g:
      #print(f"{p.name} {p.minutes}")
      resorted_players.append(p)

  #print()
  return resorted_players


# sort the players by shifts but shuffle within each group of shifts
def get_players_sorted(players):

  # Sort players by minutes in ascending order
  players.sort(key=lambda x: x.shifts)

  # Create a list of lists to store players grouped by minutes
  groups = []

  current_group = []
  current_shifts = None

  # Iterate through the sorted players and group them
  for player in players:
    if player.shifts != current_shifts:
      if current_group:
        groups.append(current_group)
      current_group = [player]
      current_shifts = player.shifts
    else:
      current_group.append(player)
  # Append the last group
  if current_group:
    groups.append(current_group)

  # go through groups and shuffle each group
  for g in groups:
    random.shuffle(g)

  # now put them all into a flat array again
  resorted_players = []
  for g in groups:
    for p in g:
      resorted_players.append(p)
  return resorted_players


### STRONGLINES
###################################


# each line in the files contains a list of players
# this function will return a list of groups of Players
def load_stronglines(players):
  stronglines = []

  # will load the input data
  with open(stronglines_file, "r") as f:
    for l in f:
      # skip comments, blank lines
      if l.count('#') > 0 or len(l.strip()) <= 0:
        continue
      names = l.strip().split(',')
      group = []

      # strip any whitespace
      for n in names:
        n = n.strip()
        p = find_player(players, n)
        group.append(p)
      stronglines.append(group)
  return stronglines


def get_players_not_in_stronglines(players, stronglines):
  nsl_players = []
  for p in players:
    match = False
    for sl in stronglines:
      for psl in sl:
        if p.name == psl.name:
          match = True
          break
    if match == False:
      nsl_players.append(p)
  return nsl_players


def print_stronglines(stronglines):
  for sl in stronglines:
    log.debug(" ")
    log.debug("strongline:")
    print_players(sl)


def print_shifts(shifts):
  for i, s in enumerate(shifts, start=1):
    log.debug(" ")
    log.debug(f"shift {i}")
    print_players(s)


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
  max_shifts = get_max_shifts(len(players))
  log.debug(shiftlimits)
  log.debug(max_shifts)

  # make 8 shifts with stronglines
  shifts = []
  for i in range(num_shifts):
    sl = stronglines[i % len(stronglines)]

    # as we do this keep track of shifts
    add_shift = False
    for p in sl:
      # consider shift limits
      # if we've hit the limit for a player, then we should
      # stop filling in stronglines
      if p.shifts < max_shifts:
        p.shifts += 1
        add_shift = True
      else:
        log.debug(f"SHIFT LIMIT REACHED: {p.name}")

    if add_shift:
      # make a copy of the stronglong so we're not putting
      # the same strongline object into multiple shifts
      # this will mess up shift counting otherwise
      shifts.append(sl.copy())

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


def fill_shifts(players, shifts):
  # assumes shifts is already an 8 shift array partially filled in with players

  # get a list of players not in the stronglines
  nsl_players = get_players_not_in_stronglines(players, stronglines)
  assert no_duplicates(nsl_players), "nsl_players has duplicates"
  #log.debug("nsl_players")
  #print_players(nsl_players)
  # get a list of players in the shifts that haven't reached the max shifts
  pnm_players = get_players_not_at_max_shifts(players, shifts)
  assert no_duplicates(pnm_players), "pnm_players has duplicates"
  #log.debug("pnm_players")
  #print_players(pnm_players)

  # combine them sort them by shifts and randomize within the groups
  next_players = get_players_sorted(nsl_players + pnm_players)

  max_shifts = get_max_shifts(len(players))

  for s in shifts:
    while len(s) < 5:  # keep going until the shift is full
      # log.debug("next_players")
      # print_players(next_players)

      # fill in the shift and increment shifts
      # but also keep on eye on max shifts to make sure there's no error
      next_players[0].shifts += 1
      assert next_players[
          0].shifts <= max_shifts, "ERROR: we've exceeded max shifts"

      #log.debug(f"ADDING {next_players[0].name}")
      s.append(next_players[0])

      # redo the player sorting so we're always picking a randomized player with
      # the least amount of shifts
      next_players = get_players_sorted(next_players)

  return shifts


def get_shifts(players, stronglines, num_shifts=8):
  shifts = get_strongline_shifts(players, stronglines, num_shifts)
  shifts = fill_shifts(players, shifts)
  return shifts


if __name__ == '__main__':
  players = load_players()
  print_players(players)

  stronglines = load_stronglines(players)
  #print_stronglines(stronglines)

  shifts = get_shifts(players, stronglines)
  print_shifts(shifts)

  if verify_shift_limits(len(players), [p.shifts for p in players]):
    log.debug("VERIFICATION PASSED")
