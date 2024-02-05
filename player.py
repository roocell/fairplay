import random
from logger import log as log
import json
from models import Player


# TODO: will have to fix the test scripts
def load(players_json):
  # load into an array of Players
  players = []

  # load json into an Array of Players
  for p in players_json:
    players.append(Player(p["name"], p["number"]))

  return players


def find(players, name):
  for p in players:
    if p.name == name:
      return p
  return None


def dump(players):
  for p in players:
    log.debug(
        f"{p.number} {p.name}: {p.shiftcnt} {p.prev} dbl {p.dbl} lts {p.lts}"
    )


# sort the players by shifts but shuffle within each group of shifts
def get_sorted(players):

  # Sort players by minutes in ascending order
  players.sort(key=lambda x: x.shiftcnt)

  # Create a list of lists to store players grouped by minutes
  groups = []

  current_group = []
  current_shifts = None

  # Iterate through the sorted players and group them
  for player in players:
    if player.shiftcnt != current_shifts:
      if current_group:
        groups.append(current_group)
      current_group = [player]
      current_shifts = player.shiftcnt
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

  # now put them all into a flat array again
  resorted_players = []
  for g in groups:
    for p in g:
      resorted_players.append(p)
  return resorted_players
