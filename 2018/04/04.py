import sys

if "__main__" == __name__:
  lt_lines = [s.strip() for s in sys.stdin]
  lt_lines.sort(reverse=True)
  ### [1518-01-12 23:57] Guard #3209 begins shift
  ### [1518-01-13 00:13] falls asleep
  ### [1518-01-13 00:21] wakes up
  d = dict()
  while lt_lines:
    toks = lt_lines.pop().strip().split()
    toklast = toks.pop().strip()

    if 'shift' == toklast:
      iguard = int(toks[-2].strip('#').strip())
      if not (iguard in d): d[iguard] = [0]*60

    elif 'asleep' == toklast:
      iasleep = int(toks[1][-3:-1])
    elif 'up' == toklast:
      iup = int(toks[1][-3:-1])
      for iminute in range(iasleep,iup): d[iguard][iminute] += 1

  mx = -1
  for iguard in d:
    sm = sum(d[iguard])
    if sm > mx:
      mx = sm
      mxguard = iguard

  lt = d[mxguard]
  mxminute = lt.index(max(lt))

  print((mxguard,mxminute,mxguard*mxminute,))

  mx = -1
  for iguard in d:
    lt = d[iguard]
    mxthis = max(lt)
    if mxthis > mx:
      mx = mxthis
      mxguard = iguard
      mxminute = lt.index(mxthis)

  print((mxguard,mxminute,mxguard*mxminute,))
