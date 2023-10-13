def no_duplicates(array):
  # Check for duplicates using a set
  if len(array) != len(set(array)):
    return False
  return True
