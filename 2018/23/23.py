import re
import os
import sys
import pprint

do_debug = "DEBUG" in os.environ
do_log23 = "LOG23" in os.environ


class OH(object):
  """Octahedron, center and vertices"""

  vzero = (0,)*3

  def __init__(self,tup4,idx):

    self.idx = idx
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

  def md(self,ohv):
    """Manhattan distance"""
    v = ohv2v(ohv)
    return (abs(self.xyz[0]-v[0])
           +abs(self.xyz[1]-v[1])
           +abs(self.xyz[2]-v[2])
           )

  def mdinside(self,ohv):
    v = ohv2v(ohv)
    result = abs(self.xyz[0] - v[0])
    if result > self.r: return False
    result += abs(self.xyz[1] - v[1])
    if result > self.r: return False
    result += abs(self.xyz[2] - v[2])
    return (result <= self.r)

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

  ohidx = 0
  with open(sys.argv[1],'r') as fin:
    ohs = list(map(lambda s:eval('OH(({0},),ohidx)'.format(re.sub("[^-\d,]","",s))),fin))
    ohidx += 1

  def keyr(oh): return oh.r

  oh_maxr = max(ohs,key=keyr)
  maxr = oh_maxr.r
  for oh in ohs:
    assert oh_maxr==oh or maxr>oh.r

  botcount = 0
  for oh in ohs:
    if oh_maxr.mdinside(oh): botcount += 1

  print('PartI:  {0}'.format(botcount))
