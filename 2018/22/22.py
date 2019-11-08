import re
import os
import sys

do_debug = "DEBUG" in os.environ
do_log22 = "LOG22" in os.environ

try: xy_mod
except:
  xy_mod,el_mod,yis0_xmult,xis0_ymult = 20183,3,16807,48271

  torch,climbing,neither = eqptyps = 'torch climbing neither'.split()
  rocky,wet,narrow = regtyps = 'rocky wet narrow'.split()
  c_rwn = '.=|'

  reg2eqp = dict([(regtyps[i],(eqptyps[i],eqptyps[(i+1)%el_mod],),)
                  for i in range(el_mod)
                 ])

  depth = None
  xytarget = None
  gieltys = dict()

class R(object):
  """Region"""
  class_depth = 0
  def __init__(self,xy,geoidx):
    global depth
    self.x,self.y = xy
    self.update(geoidx)

  def update(self,geoidx):
    self.geoidx = geoidx
    self.erolvl = (geoidx + depth) % xy_mod
    self.regtyp = self.erolvl % el_mod
    self.regchr = c_rwn[self.regtyp]


if "__main__" == __name__ and sys.argv[1:]:

  """
  depth: 5355
  target: 14,796
  """

  rgx_input = re.compile('^\W*([a-zA-Z0-9_]*)\W*:\W*(\d+)\W*(,(\d*))*W*$')

  dt_inputs = dict()

  with open(sys.argv[1],'r') as fin:
    for rawline in fin:
      match = rgx_input.match(rawline)
      if match is None: continue
      toks = match.groups()
      L = len(toks)
      if 4!=L: continue
      if toks[3] is None: dt_inputs[toks[0]] = int(toks[1])
      else: dt_inputs[toks[0]] = [int(toks[1]),int(toks[3])]

  depth = dt_inputs['depth']
  xtarget,ytarget = xytarget = dt_inputs['target']

  giformula = lambda ael,bel: ((ael * bel))

  def need(xy):
    global gieltys
    x,y = xy
    if y in gieltys and x in gieltys[y]: return gieltys[y][x]

    if x:
      if y: geoidx = giformula(need([x-1,y]).erolvl,need([x,y-1]).erolvl)
      else: geoidx = giformula(x,yis0_xmult)
    elif y: geoidx = need([x,y-1]).geoidx + xis0_ymult
    else: geoidx = 0

    if xy==xytarget: geoidx = 0

    result = R(xy,geoidx)

    if not y in gieltys: gieltys[y] = dict()
    gieltys[y][x] = result

    return result

  gieltys = dict()
  need([xtarget+5,ytarget+5,])

  rsklvl = 0
  for y in sorted(gieltys.keys()):
    gieltysy = gieltys[y]
    for x in sorted(gieltysy.keys()):
      if x <= xtarget and y <= ytarget: rsklvl += gieltysy[x].regtyp
      if not do_debug: continue
      sys.stdout.write(gieltysy[x].regchr)
    if do_debug:
      sys.stdout.write('\n')

  print(rsklvl)
