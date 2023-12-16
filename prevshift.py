from logger import log as log
import player

enabled = False


def load(players, prevshifts_json):
  # will load the input data
  for pv in prevshifts_json:
    p = player.find(players, pv["name"])
    p.prev = pv["value"]
  return players
