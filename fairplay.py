import random
import os

# input
# players.txt  - a list of players
# games.txt - a list of comma separated values game#,player,minutes
#           - this is a running file of all the minutes played by a player for all games
# output
#   dumps the recommended shifts for the next game
#   games_out.txt - adjusted games file that can be used for the next time

games_file = "games.txt"
games_out_file = "games_out.txt"
players_file = "players.txt"
stronglines_file = "stronglines.txt"
stronglines_enabled = False


class Player:

  def __init__(self, name):
    self.name = name
    self.minutes = 0
    self.shifts = 0


# Read player data from players.txt and store in a list of Player objects
players = []


# return an array of players given an array of player names
def getplayers(players, pnames):
  plist = []
  for n in pnames:
    for p in players:
      if p.name == n:
        plist.append(p)
  return plist


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


# return an array of players in a strongline if the given player is in a strongline
def strongline(players, player):
  if os.path.exists(stronglines_file):
    with open(stronglines_file, "r") as f:
      for l in f:
        strongdata = l.strip().split(", ")
        strongplayers = getplayers(players, strongdata)
        for sp in strongplayers:
          if player.name == sp.name:
            print(player.name + " is in a strongline with " + l + "\n")
            return strongplayers
  print(player.name + " is NOT in a strong group" + "\n")
  return []  # an empty array


# Function to randomly pick multiple groups of players for the next game
def pick_multiple_groups(players, group_size=5, num_shifts=8):
  groups = []
  max_shifts = int(len(players) / group_size)

  for _ in range(num_shifts):
    players = get_players_sorted(players)
    min_minutes = min(player.minutes for player in players)
    players_with_min_minutes = [
        player for player in players if player.minutes == min_minutes
    ]

    # print("shift" + str(len(groups) + 1) + " min minutes players")
    # for p in players_with_min_minutes:
    #   print(p.name)
    # print("\n")

    # if the player already has max shifts, then remove him from selection
    for p in players_with_min_minutes.copy():
      if p.shifts >= max_shifts:
        print(f"removing {p.name}")
        players_with_min_minutes.remove(p)

    # pick a group
    group = players_with_min_minutes[:group_size]

    # adjust group for stronglines
    # if anyone in the group is in a strongline, pick that strongline and 2 others
    strong_group = []
    if stronglines_enabled:
      for p in group:
        strongplayers = strongline(players, p)
        if len(strongplayers) > 0:
          strong_group = strongplayers

          # remove these players from the original list
          players = [
              player for player in players if player not in strongplayers
          ]
          players = get_players_sorted(players)

          # add more players to fill out a line
          # TODO: we should eliminate other strong players from here?
          strong_group += players[:5 - len(strongplayers)]
          break

    if len(strong_group) > 0:
      group = strong_group
    for p in group:
      p.minutes += 4

    # if this was a group less than group size - it means that there wasn't enough players
    # with min minutes to form a group
    # just - reiterate - and it'll automatically keep increasing this players minutes until
    # he gets into the next group and forms a 5
    if len(group) < group_size:
      continue

    groups.append(group)

    # adjust shifts
    for p in group:
      p.shifts += 1

  return groups


def get_groups():
  # Call the function to pick groups for the next game
  next_game_groups = pick_multiple_groups(players)

  print("get_groups" + str(len(next_game_groups)))
  for shift, group in enumerate(next_game_groups, start=1):
    print(f"\nShift {shift} - Players:")
    for player in group:
      print(f"{player.name} {player.minutes}")

  print()
  f = open(games_out_file, "w")
  for p in players:
    print(f"{p.name} {p.minutes} {p.shifts}")
    if p.shifts > 3:
      print(">>>>>>>ERROR: too many shifts<<<<<<<<<<<<")
    # dump player,minutes to file (can be used to determine shifts for next game)
    f.write(f"{p.name},{p.minutes}\n")
  print()
  return next_game_groups


def print_groups(groups):
  # Print out the groups
  print(len(groups))
  for shift, group in enumerate(groups, start=1):
    print(f"\nShift {shift} - Players:")
    for player in group:
      print(f"{player.name} {player.minutes}")


def get_players():
  return players


def load_data():
  global players

  players = []

  # will load the input data
  with open(players_file, "r") as f:
    for l in f:
      player_name = l.strip()
      players.append(Player(player_name))

  # Read game data from games.txt and tally up the minutes played for each player
  if os.path.exists(games_file):
    with open(games_file, "r") as f:
      for line in f:
        game_data = line.strip().split(",")
        game_player, minutes = game_data[0], int(game_data[1])

        # Find the corresponding player object and update their minutes
        for player in players:
          if player.name == game_player:
            player.minutes += minutes
  else:
    print("no games input file")

  # Sort the players by their total minutes played (from least to most)
  players.sort(key=lambda x: x.minutes)

  # Print out the total minutes played for each player
  for player in players:
    print(f"{player.name}: {player.minutes} minutes played")
  print("\n\n\n")
