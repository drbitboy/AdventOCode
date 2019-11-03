import os
import sys
import traceback

do_debug = 'DEBUG' in os.environ

if "__main__" == __name__:
  d = dict()
  ct = 0
  st_claims = set()
  for rawclaim in sys.stdin:
    #1397 @ 453,308: 19x24
    sclaim,sgeom = rawclaim.strip().split('@')
    claim = sclaim.split('#')[1].strip()
    slt,swh = sgeom.split(':')
    left,top = list(map(int,slt.split(',')))
    wid,hgt = list(map(int,swh.split('x')))

    no_doubles = True

    for col in range(left,left+wid):
      if not (col in d): d[col] = dict()
      dcol = d[col]
      for row in range(top,top+hgt):
        if not (row in dcol):
          dcol[row] = [1,claim]
        else:
          no_doubles = False
          if dcol[row][1] in st_claims: st_claims.remove(dcol[row][1])
          if 1 == dcol[row][0]:
            dcol[row][0] = 2
            ct += 1

    if no_doubles: st_claims.add(claim)

  print(ct)
  print(st_claims)
          
