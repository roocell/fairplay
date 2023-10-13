from logger import log as log
import player

enabled = False
prevshifts_file = "prevshifts.txt"


def load(players):
  # will load the input data
  with open(prevshifts_file, "r") as f:
    for l in f:
      # skip comments or blank lines
      if l.count('#') > 0 or len(l.strip()) <= 0:
        continue
      parts = l.strip().split(',')
      name = parts[0].strip()
      prevshifts = parts[1].strip()
      p = player.find(players, name)
      p.prev = prevshifts
  return players
