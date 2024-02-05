from logger import log as log
import player

# each line in the files contains a list of players
# this function will return a list of groups of Players
def load(players, groupsjson):
  #groups_colours = ["#f0d5aa", "#cff6ff", "#e1ffcf", "#f1d9ff", "#ffd9d9"]
  groups_colours = ["#777777", "#999999", "#99CEAC", "#33B0AF", "#2E6C9D"]
  groups = []

  # load into an array groups
  # array of sets of Players
  for sl in groups_json:
    group = []
    colour = groups_colours.pop()
    for name in sl:
      p = player.find(players, name)
      if (p == None):
        log.debug(f"couldn't find player {name}")
        # this can happen if a player is on a group, but has been removed from the game
        # just leave them out of the group
      else:
        # assign a color to the players in this group - so they can appear 'together' on web
        p.colour = colour
        group.append(p)
    groups.append(group)
  return groups


# need to reload groups if roster is adjusted
# might have to remove players
# TODO: need UI to adjust groups
def reload(players, groups):
  groups_new = []
  for g in groups:
    group = []
    for p in g:
      if (player.find(players, p.name) == None):
        log.debug(f"couldn't find player {p.name}")
        # this can happen if a player is on a groups, but has been removed from the game
        # just leave them out of the group
      else:
        group.append(p)
    groups_new.append(group)
  return groups_new


def get_players_not_in_groups(players, groups):
  nsl_players = []
  for p in players:
    match = False
    for g in groups:
      for psl in g:
        if p.name == psl.name:
          match = True
          break
    if match == False:
      nsl_players.append(p)
  return nsl_players


def dump(groups):
  for sl in groups:
    log.debug(" ")
    log.debug("groups:")
    player.dump(sl)
