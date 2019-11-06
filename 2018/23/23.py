import re
import os
import sys
import pprint

do_debug = "DEBUG" in os.environ
do_log23 = "LOG23" in os.environ


class OH(object):
  """Octahedron, center and vertices"""

  vzero = (0,)*3

  def __repr__(self): return 'OH({0},{1})'.format(self.idx,self.orig_idx)

  def __init__(self,tup4,orig_idx):

    self.orig_idx = orig_idx
    self.idx = -1
    self.xyz = tup4[:3]
    self.r = (4==len(tup4)) and tup4[3] or 0 

    if 0==self.r:
      self.verts = [self.xyz] * 6
      return

    self.verts = list()
    for i in range(6):
      isplus = not ((i&1) and True or False)
      ixyzbit = i & 6
      vertidx=0
      while ixyzbit > 1:
        ixyzbit >>= 1
        vertidx += 1
      self.verts.append(vadd(self,idx=vertidx,offset=(isplus and self.r or -self.r)))

    self.intersecting_ohs = set()

  def md(self,ohv):
    """Manhattan distance"""
    v = ohv2v(ohv)
    return (abs(self.xyz[0]-v[0])
           +abs(self.xyz[1]-v[1])
           +abs(self.xyz[2]-v[2])
           )

  def ohintersect(self,ohother):
    return self.mdinside(ohother.xyz,deltar=ohother.r)

  def mdinside(self,ohv,deltar=False):
    v = ohv2v(ohv)
    result = abs(self.xyz[0] - v[0])
    r = self.r + (deltar and deltar or 0)
    if result > r: return False
    result += abs(self.xyz[1] - v[1])
    if result > r: return False
    result += abs(self.xyz[2] - v[2])
    return (result <= r)

def ohv2v(ohvin):
  if isinstance(ohvin,OH): return ohvin.xyz
  return ohvin

def vadd(ohv1,ohv2=OH.vzero,idx=-1,offset=0):
  v1 = ohv2v(ohv1)
  v2 = ohv2v(ohv2)
  return ((v1[0]+v2[0] + (idx==0 and offset or 0))
         ,(v1[1]+v2[1] + (idx==1 and offset or 0))
         ,(v1[2]+v2[2] + (idx==2 and offset or 0))
         )

####################################
if "__main__" == __name__ and sys.argv[1:]:

  ohs = list()
  with open(sys.argv[1],'r') as fin:
    ohline = 0
    for s in fin:
      tup4 = eval('({0},)'.format(re.sub("[^-\d,]","",s)))
      ohs.append(OH(tup4,ohline))
      ohline += 1

  L = len(ohs)

  def keyr(oh): return oh.r

  ohs.sort(key=keyr)

  for idx,oh in enumerate(ohs): oh.idx = idx

  oh_maxr = ohs[-1]

  print(oh_maxr.__dict__)

  maxr = oh_maxr.r
  for oh in ohs:
    assert oh_maxr==oh or maxr>oh.r

  botcount = 0
  for oh in ohs:
    if oh_maxr.mdinside(oh): botcount += 1

  print('PartI:  {0}'.format(botcount))

  for oh in ohs:
    for i,oh2 in enumerate(ohs):
      if oh.ohintersect(oh2):
        oh.intersecting_ohs.add(i)

  lens = [(len(oh.intersecting_ohs),oh,oh.intersecting_ohs,) for i,oh in enumerate(ohs)]
  
  st_subsets = set()

  sys.stdout.flush()

  for ioh,oh in enumerate(ohs):
    st = oh.intersecting_ohs
    for idx in st:
      st = st.intersection(ohs[idx].intersecting_ohs)
      if not len(st): break
    if len(st): st_subsets.add((len(st),tuple(sorted(st)),))
    if ((ioh+1)%100): continue
    sys.stderr.write('{0}...'.format(ioh+1))
    sys.stderr.flush()

  sys.stderr.write('done\n')
  sys.stderr.flush()

  Ltups = sorted(st_subsets)
  Lmax = Ltups[-1][0]
  Lmaxtups = list()
  while Ltups and Ltups[-1][0] == Lmax: Lmaxtups.append(Ltups.pop())

  partII = min([max([ ohs[idx].md(OH.vzero)-ohs[idx].r
                      for idx in tup
                    ]
                   )
                for L,tup in Lmaxtups
               ]
              )
    
  print('PartII:  {0}'.format(partII))
