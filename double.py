from logger import log as log


# check for consequtive shifts
def check_consecutive(players, shifts):
  # clear all doubleshifts
  for p in players:
    p.doubleshifts = [0] * 8

  for i, s in enumerate(shifts, start=0):
    if i == len(shifts) - 1:
      continue  # skip last one
    nextshift = shifts[i + 1]
    for p in s:
      if p in nextshift:
        log.error(f"double shift for {p.name} in shift {i+1}")
        p.doubleshifts[i + 1] = 1
