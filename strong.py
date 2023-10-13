from logger import log as log
import player

### STRONGLINES
###################################
enabled = True
stronglines_file = "stronglines.txt"


# each line in the files contains a list of players
# this function will return a list of groups of Players
def load(players):
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
        p = player.find(players, n)
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
