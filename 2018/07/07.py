import os
import sys
import math

do_debug = "DEBUG" in os.environ

if "__main__" == __name__ and sys.argv[1:]:

  dt_prereq = dict()
  with open(sys.argv[1],'r') as fin:
    for rawline in fin:
      toks = rawline.strip().split()
      lo,hi = toks[1],toks[-3]
      if not (hi in dt_prereq): dt_prereq[hi] = set()
      if not (lo in dt_prereq): dt_prereq[lo] = set()
      dt_prereq[hi].add(lo)

  st_keys = set(dt_prereq.keys())

  lt_out = list()
  st_out = set()

  while st_keys:
    lt_possibles = list()
    for one in st_keys:
      if dt_prereq[one].issubset(st_out): lt_possibles.append(one)
    lt_possibles.sort(reverse=True)
    one = lt_possibles.pop()
    lt_out.append(one)
    st_out.add(one)
    st_keys.remove(one)

  print('PartI:  {0}'.format(''.join(lt_out)))


  lt_out = list()
  st_out = set()

  n_workers = int(os.environ.get("WORKERS",5))
  backlogs = [list() for iworker in range(n_workers)]
  if do_debug: print(dict(n_workers=len(backlogs)))

  time_offset = 1 + int(os.environ.get("TIME_OFFSET",60)) - ord('A')

  st_keys = set(dt_prereq.keys())
  T = 0
  while st_keys or sum([len(backlog) for backlog in backlogs]):

    lt_possibles = list()
    for one in st_keys:
      if dt_prereq[one].issubset(st_out): lt_possibles.append(one)

    lt_possibles.sort(reverse=True)

    for backlog in backlogs:
      if not lt_possibles: break
      if backlog: continue
      one = lt_possibles.pop()
      backlog.extend([one] * (time_offset + ord(one)))
      st_keys.remove(one)
      if do_debug: print(dict(Start=(T,one,)))

    T += 1

    finished = list()
    for backlog in backlogs:
      if not backlog: continue
      popped = backlog.pop()
      if not backlog:
        finished.append(popped)
        if do_debug: print(dict(End=(T,popped,)))

    lt_out.extend(finished)
    list(map(st_out.add,finished))


  print('PartII:  {0} [{1}]'.format(T, ''.join(lt_out)))

