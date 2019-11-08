import re
import os
import sys
from blist import sortedlist

### Jargon:
###   gi:  Geology Index
###   el/EL: Erosion level
###   rt: Region type (rocky, wet, narrow)
###   et: Equipment Type (torch, climbing gear, neither)

########################################################################
try: xy_mod
except:

  ### Constants (not all are used)

  do_debug = "DEBUG" in os.environ
  do_log22 = "LOG22" in os.environ

  xy_mod,yis0_xmult,xis0_ymult = 20183,16807,48271

  et_cost = 7     ### Cost to change et within same node
  step_cost = 1   ### Cost to step between adjacent nodes with same et

  ### - Region types, and one-letter characters for same
  rocky,wet,narrow = rts = 'rocky. wet= narrow|'.split()
  rtchrs = [s[-1] for s in rts]

  ### - Modulus to convert from (geology index + xymod) to erosion level
  el_mod = len(rts)

  ### - Equipment types
  torch,climbing,neither = s_ets = 'torch climbing neither'.split()

  ### - Acceptable equipment within each region type
  ###   - rocky:  allows torch and climbing gear
  ###   - wet:  allows climbing gear and neither
  ###   - narrow:  allows neither and torch

  rt2et = [(i,(i+1)%el_mod,) for i in range(el_mod)]

  ### - Regions to which equipment can move
  et2rt = [(i,(i+el_mod-1)%el_mod,) for i in range(el_mod)]

  ### Globals
  depth = None


########################################################################
class R(object):
  """Region"""

  def __init__(self,x,y,gi):
    self.x,self.y,self.rnodes = x,y,list()
    self.update(gi)

  def addnode(self,new_rnode):
    if self.hasnode(new_rnode): return
    self.rnodes.append(new_rnode)

  def hasnode(self,rnode_to_check):
    for rnode in self.rnodes:
      if rnode_to_check is rnode: return True
    return False

  def update(self,gi):
    global depth
    self.gi = gi
    self.el = (gi + depth) % xy_mod
    self.rt = self.el % el_mod
    self.rtchr = rtchrs[self.rt]


########################################################################
class Rnode(object):
  """Region + tool equipped"""

  INFINITY = None

  def __init__(self,r,et):

    global y_shift
    global x_shift
    global el_shift

    if Rnode.INFINITY is None:
      global xtarget
      global ytarget
      ### Maximum distance per step is 8 (1 + 7 for equipment change),
      ### so set INFINITY to 16 times minimum number of steps
      Rnode.INFINITY = (xtarget + ytarget) << 4

    assert et in rt2et[r.rt]
    self.r,self.et = r,et
    self.dist = Rnode.INFINITY
    self.st_cn = set()

    self.hash = (self.r.y << y_shift
            ) | (self.r.x << x_shift
            ) | (self.et << el_shift
            )

    self.r.addnode(self)


  def dist_key(self): return (-self.dist,-self.hash,)

  def __hash__(self): return self.hash
  def __eq__(self,otherRnode): return self.hash == otherRnode.hash

  def connect(self,otherRnode,do_reverse=False):
    """Connect Rnodes with edges"""

    if self is otherRnode: return   ### Do not connect node to itself

    if self.r is otherRnode.r:      ### Same node ...

      if self.et != otherRnode.et:  ### ... only connect to different et

        self.st_cn.add((otherRnode,et_cost))

      else: return        ### No valid connection; short-circuit reverse

    else:                           ### Adjacent nodes ...

      if self.et == otherRnode.et:  ### ... only connect to same et


        self.st_cn.add((otherRnode,step_cost))

      else: return        ### No valid connection; short-circuit reverse

    if do_reverse: otherRnode.connect(self)


########################################################################
if "__main__" == __name__ and sys.argv[1:]:

  ### Parse input file

  ### - Typical input
  """
  depth: 5355
  target: 14,796
  """

  ### - Regex to match those lines
  rgx_input = re.compile('^\W*([a-zA-Z0-9_]*)\W*:\W*(\d+)\W*(,(\d*))*W*$')

  ### - Create dict to hold inputs

  dt_inputs = dict()

  ### - Parse a line at a time

  with open(sys.argv[1],'r') as fin:
    for rawline in fin:
      match = rgx_input.match(rawline)
      if match is None: continue
      toks = match.groups()
      L = len(toks)
      if 4!=L: continue
      if toks[3] is None: dt_inputs[toks[0]] = int(toks[1])
      else: dt_inputs[toks[0]] = [int(toks[1]),int(toks[3])]

  ### - Extract relevant data:  depth and target coordinates

  depth = dt_inputs['depth']
  xtarget,ytarget = dt_inputs['target']


  ##################################
  def n2sm(n,base_shift=0):
    """
Convert number to bit-width and mask
- This is for hash, which will be

    (Y << y_shift) | (X << x_shift) | (EL << el_shift)

"""
    ibit,ishift = 1,0
    while ibit <= n:
      ibit <<= 1
      ishift += 1
    return ishift+base_shift,(ibit-1)<<base_shift


  ##################################
  ### Setup to build hash for Rnode objects

  el_shift = 0
  x_shift,el_mask = n2sm(el_mod,base_shift=el_shift)
  y_shift,x_mask = n2sm(xtarget,base_shift=x_shift)
  full_shift,y_mask = n2sm(ytarget,base_shift=y_shift)

  if do_debug:
    print(dict(full_x_y_el_shifts=(full_shift,y_shift,x_shift,el_shift,)))
    print('{3}x_y_el_masks=({0:08x},{1:08x},{2:08x}){4}'.format(y_mask,x_mask,el_mask,'{','}',))

  ### Formula for Geology Index
  giformula = lambda ael,bel: ((ael * bel))


  ##################################
  def need(x,y):
    """Recursive creator of instances of R class"""

    global gielrts
    global Q

    ### Use R instance for this x,y pair from dict if it is there

    if y in gielrts and x in gielrts[y]: return gielrts[y][x]

    ### Get adjacend R instances closer to start position

    if y: xym1 = need(x,y-1)
    else: xym1 = None
    if x: xm1y = need(x-1,y)
    else: xm1y = None

    ### Calculate gi (Geometry Index) for this x,y pair

    if x:
      if y: gi = giformula(xm1y.el,xym1.el)
      else: gi = xm1y.gi + yis0_xmult        ### giformula(x,yis0_xmult)
    elif y: gi = xym1.gi + xis0_ymult        ### giformula(y,xis0_ymult)
    else: gi = 0

    ### Special case:  reset gi at target

    if x==xtarget and y==ytarget: gi = 0

    ### Instantiate an R object

    result = R(x,y,gi)

    ### For the allowable ets (Equipment Types) ...

    for et in rt2et[result.rt]:

      ### ... Instantiate an Rnode object at this R object's position
      ###     with that et

      rnode = Rnode(result,et)

      for radj in (xym1,xm1y,):

        if isinstance(radj,R) and radj.rt in et2rt[et]:

          ### For each adjacent Rnode object ...

          for adjRnode in radj.rnodes:

            ### ... connect rnode to it

            rnode.connect(adjRnode,do_reverse=True)

      ### Add instantiated Rnode object to sorted list Q

      Q.add(rnode)


    ### For the rnodes just instantiated and stored in result.rnodes ...
    for rnode in result.rnodes:

      for otherRnode in result.rnodes:

        if not (rnode is otherRnode):

          ### ... connect them to each other

          rnode.connect(otherRnode,do_reverse=True)

    ### Place result into dict at position x,y

    if not y in gielrts: gielrts[y] = dict()
    gielrts[y][x] = result

    ### Return instantiated R object

    return result

    ### End of [def need(...)]
    ################################


  ######################################################################
  ### Setup complete, start algorithm

  ### Globals

  gielrts = dict()
  Q = sortedlist([],key=lambda r:r.dist_key())

  ### Instantiate R and Rnode objects
  ### - Add Rs as padding beyond target XY coordinates, in case it is
  ###   faster to go beyond those limits to get to target.  35 is a
  ###   guess works for the author; values as low as 17 gave the same
  ###   answer.

  need(xtarget+35,ytarget+35)

  ### Part I:  calculate risk level;, sum of erosion levels between
  ###          origin and target

  rsklvl = 0
  for y in sorted(gielrts.keys()):
    gielrtsy = gielrts[y]
    for x in sorted(gielrtsy.keys()):
      if x <= xtarget and y <= ytarget: rsklvl += gielrtsy[x].rt
      if not do_debug: continue
      sys.stdout.write(gielrtsy[x].rtchr)
    if do_debug:
      sys.stdout.write('\n')

  print('PartI:  {0}'.format(rsklvl))

  ### End Part I
  ######################################################################

  def decrease_dist(rnode,new_dist):
    """Change distance of Rnode object in sorted list Q, while
maintining correct position within Q
"""
    global Q
    Q.remove(rnode)         ### Delete from Q
    rnode.dist = new_dist   ### Adjust distance
    Q.add(rnode)            ### Add back to Q

  ### Find Rnode starting point:  x=0; y=0; s_et=torch

  rsource = gielrts[0][0]

  for rnode in rsource.rnodes:
    if s_ets[rnode.et] == torch: break

  assert s_ets[rnode.et] == torch or dict()[s_ets[rnode.et]]
  assert rnode.dist == Rnode.INFINITY or dict()[rnode.dist]

  ##################################
  ### Djikstra's Algorithm
  ### cf. https://en.wikipedia.org/wiki/Dijkstra's_algorithm
  ##################################

  ### Set the source Rnode's distance to zero, including re-positioning
  ### it within sortedlist Q

  decrease_dist(rnode,0)

  while len(Q):                                ### Loop over Rnodes in Q

    u_rnode = Q.pop()         ### Remove u, vertex with min dist, from Q


    if u_rnode.r is gielrts[ytarget][xtarget]:   ### If X,Y target hit,
      if s_ets[u_rnode.et] == torch:             ### and torch equipped,
        break                                    ### then exit loop

    distu = u_rnode.dist

    for v_conn,v_len in u_rnode.st_cn:   ### For each neighbor of v of u
      if v_conn.dist <= distu: continue  ### - skip v if not in Q
      alt = distu + v_len                ### Min distance to v through u
      if alt < v_conn.dist:              ### If this improves dist to v,
        decrease_dist(v_conn,alt)        ### ... then decrease distance

  
  print('PartII:  {0}'.format(u_rnode.dist))
