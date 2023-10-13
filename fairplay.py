import random
import os
from logger import log as log
from shift_limits import get_shift_limits, get_max_shifts, verify_shift_limits
from utils import no_duplicates
import player
import strong

# input
# players.txt  - a list of players
# games.txt - a list of comma separated values game#,player,minutes
#           - this is a running file of all the minutes played by a player for all games
# output
#   dumps the recommended shifts for the next game
#   games_out.txt - adjusted games file that can be used for the next time

roster_file = "roster.out"

prevshift_enabled = False
prevshifts_file = "prevshifts.txt"


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
      # log.debug("next_players")
      # player.dump(next_players)

      # fill in the shift and increment shifts
      # but also keep on eye on max shifts to make sure there's no error
      next_players[0].shifts += 1
      assert next_players[
          0].shifts <= max_shifts, "ERROR: we've exceeded max shifts"

      #log.debug(f"ADDING {next_players[0].name}")
      s.append(next_players[0])

      # redo the player sorting so we're always picking a randomized player with
      # the least amount of shifts
      next_players = player.get_sorted(next_players)

  return shifts


def get_shifts(players, stronglines, num_shifts=8):
  shifts = get_strongline_shifts(players, stronglines, num_shifts)
  shifts = fill_shifts(players, shifts)
  return shifts


if __name__ == '__main__':
  players = player.load()
  player.dump(players)

  stronglines = strong.load(players)
  #strong.dump(stronglines)

  shifts = get_shifts(players, stronglines)
  print_shifts(shifts)

  if verify_shift_limits(len(players), [p.shifts for p in players]):
    log.debug("VERIFICATION PASSED")
