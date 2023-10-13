# every game has players missing
# this will tell you how many shifts players should get to be fair
# [number of players] = ...(number of shifts, number of players)
shift_numbers = dict()
shift_numbers[15] = [(3, 10), (2, 5)]
shift_numbers[14] = [(3, 12), (2, 2)]
shift_numbers[13] = [(4, 1), (3, 12)]
shift_numbers[12] = [(4, 4), (3, 8)]
shift_numbers[11] = [(4, 7), (3, 4)]
shift_numbers[10] = [(4, 10)]
shift_numbers[9] = [(5, 4), (4, 5)]
shift_numbers[8] = [(6, 4), (4, 4)]
shift_numbers[7] = [(6, 5), (5, 2)]
shift_numbers[6] = [(7, 5), (5, 1)]
shift_numbers[5] = [(8, 5)]


# returns an array of shift_cnt, players
def get_shift_limits(num_players):
  return shift_numbers[num_players]


def get_max_shifts(num_players):
  max = 0
  for t in shift_numbers[num_players]:
    if t[0] > max:
      max = t[0]
  return max


# shift_list is an array of integers that represents
# the shifts for the players
def verify_shift_limits(num_players, shift_list):
  # count how many of each we have
  cnts = dict()
  for c in range(2, 9):
    cnts[c] = shift_list.count(c)

  for t in shift_numbers[num_players]:
    #print(f"{cnts[t[0]]} {t[1]}")
    assert cnts[t[0]] == t[1],  \
      f"ERROR filled shifts do not comply to shift limits"
  return True
