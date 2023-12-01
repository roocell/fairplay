import random
from logger import log as log
import prevshift
import json


# use a class encoder in order to dump python classes
class PlayerEncoder(json.JSONEncoder):

  def default(self, obj):
    if isinstance(obj, Player):
      # Return a dictionary representation of your class
      return obj.__dict__
    return super(PlayerEncoder, self).default(obj)


class Player:

  def __init__(self, name, number):
    self.name = name
    self.number = number
    self.shifts = 0
    self.prev = 0  # previous shifts
    self.colour = "white"
    self.doubleshifts = [0] * 8  # an array of bools for each shift
    self.violates = 0  # violates max shifts
    self.lockedtoshift = [0] * 8  # an array of bools for each shift

# TODO: will have to fix the test scripts
def load(players_json, prevshifts_json):
  # load into an array of Players
  players = []

  # load json into an Array of Players
  for p in players_json:
    players.append(Player(p["name"], p["number"]))

  if prevshift.enabled:
    prevshift.load(players, prevshifts_json)

  return players


def find(players, name):
  for p in players:
    if p.name == name:
      return p
  return None


def dump(players):
  for p in players:
    log.debug(
        f"{p.number} {p.name}: {p.shifts} {p.prev} {p.doubleshifts} {p.lockedtoshift}"
    )


# sort the players by shifts but shuffle within each group of shifts
def get_sorted(players):

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
  # if using previous shift, sort ascending order
  # so that players with fewer previous shifts get favoured
  for g in groups:
    random.shuffle(g)
    if prevshift.enabled:
      log.debug("sorting with PREV SHIFT")
      g.sort(key=lambda x: x.prev)

  # now put them all into a flat array again
  resorted_players = []
  for g in groups:
    for p in g:
      resorted_players.append(p)
  return resorted_players
