from logger import log as log
import player

### STRONGLINES
###################################
enabled = True


# each line in the files contains a list of players
# this function will return a list of groups of Players
def load(players, stronglines_json):
  stronglines = []

  # load into an array stronglines
  # array of sets of Players
  for sl in stronglines_json:
    group = []
    for name in sl:
      p = player.find(players, name)
      if (p == None):
        log.debug(f"couldn't find player {name}")
        # this can happen if a player is on a strongline, but has been removed from the game
        # just leave them out of the strongline
      else:
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


def dump(stronglines):
  for sl in stronglines:
    log.debug(" ")
    log.debug("strongline:")
    player.dump(sl)
