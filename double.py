from logger import log as log


# check for consequtive shifts
def check_consecutive(players):
  for p in players:
    if p.shifts > 0:
      log.debug(f"{p.number} {p.name}: {p.shifts} consecutive shifts")
      return True
  return False
