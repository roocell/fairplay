import random
from logger import log as log

players_file = "players.txt"

# PLAYERS
##################################################


class Player:

  def __init__(self, name, number):
    self.name = name
    self.number = number
    self.shifts = 0


def load():
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


def find(players, name):
  for player in players:
    if player.name == name:
      return player
  return None


def dump(players):
  for p in players:
    log.debug(f"{p.number} {p.name}: {p.shifts}")


def get_sorted(players):
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
  for g in groups:
    random.shuffle(g)

  # now put them all into a flat array again
  resorted_players = []
  for g in groups:
    for p in g:
      resorted_players.append(p)
  return resorted_players
