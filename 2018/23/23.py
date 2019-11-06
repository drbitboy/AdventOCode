import re
import os
import sys
import pprint

do_debug = "DEBUG" in os.environ
do_log23 = "LOG23" in os.environ


class OH(object):
  """Octahedron (OH), i.e. sphere with Manhattan Distance (MD) radius.

For solving Advent of Code, 2018 day 23

"""

  vzero = (0,)*3            ### Zero vector


  ####################################
  def __repr__(self):
    """Use indices for output"""

    return 'OH({0},{1})'.format(self.idx,self.orig_idx)


  ####################################
  def __init__(self,tup4,orig_idx):
    """Constructor:  tup4 = (Xcenter, Ycenter, Zcenter, Radius,);
orig_idx = index for use by the user.

"""

    ### Save the original index (offset to line in file)
    ### Set the other index to -1; it will be sort position

    self.orig_idx = orig_idx
    self.idx = -1

    ### Coordinates of vector from origin to center
    ### Radius (manhattan distance) to edge of range

    self.x,self.y,self.z = self.xyz = tup4[:3]
    self.r = (4==len(tup4)) and tup4[3] or 0

    ### Create a set for OHs that intersect this one

    self.intersecting_ohs = set()


  ##################################
  def md(self,ohv):
    """Manhattan distance relative to """
    v = ohv2v(ohv)
    return (abs(self.x-v[0])
           +abs(self.y-v[1])
           +abs(self.z-v[2])
           )


  ##################################
  def ohintersect(self,ohother):
    """Return True if other OH intersects this OH at any point"""
    return self.mdinside(ohother.xyz,deltar=ohother.r)


  ##################################
  def mdinside(self,ohv,deltar=False):
    """Return True if ohv (OH or vector) is within Manhattan distance of
(self.r + deltar) of self.xyz

"""
    v = ohv2v(ohv)
    result = abs(self.x - v[0])
    r = self.r + (deltar and deltar or 0)
    if result > r: return False
    result += abs(self.y - v[1])
    if result > r: return False
    result += abs(self.z - v[2])
    return (result <= r)


########################################################################
def ohv2v(ohvin):
  """Argument ohvin may be either a vector or an OH instance; transform
either to vector; use OH().xyz (center) if ohvin is an OH

"""
  if isinstance(ohvin,OH): return ohvin.xyz  ### Use OH center
  return ohvin                               ### Assume ohvin is vector

  ### End of OH class
  ######################################################################


########################################################################
if "__main__" == __name__ and sys.argv[1:]:

  ohs = list()                                    ### Create list of OHs
  with open(sys.argv[1],'r') as fin:           ### Open file for reading
    ohline = 0                         ### Initialze line offset to zero
    for s in fin:                                    ### Loop over lines
      t4 = eval('({0},)'.format(re.sub("[^-\d,]","",s)))  ### Parse line
      ohs.append(OH(t4,ohline))  ### Make OH w/parsed tuple, add to list
      ohline += 1                              ### Increment line offset

  ohs.sort(key=lambda loh:-loh.r)     ### Sort by decreasing (MD) radius

  for idx,oh in enumerate(ohs): oh.idx = idx     ### Load sorted indices

  oh_maxr = ohs[0]                           ### OH with maximum radius

  print(oh_maxr.__dict__)

  maxr = oh_maxr.r
  for oh in ohs:
    assert oh_maxr==oh or maxr>oh.r     ### Ensure there is 1 max radius

  botcount = len([None                      ### Count OHs inside oh_maxr
                  for oh in ohs
                  if oh_maxr.mdinside(oh)
                 ])

  print('PartI:  {0}'.format(botcount))                ### Part I result

  ######################################################################
  ######################################################################

  for oh in ohs:                 ### Find all OHs that intersect each OH
    for oh2 in ohs:
      if oh is oh2 or oh.ohintersect(oh2):
        oh.intersecting_ohs.add(oh2.idx)  ### Save intersecting OH index

  st_subsets = set()                     ### Initialize set to hold sets

  sys.stdout.flush()

  Lmx = 0             ### Keep track of size of maximum set found so far

  ### From the problem statement, this is the maximum number of nanobots
  ### found so far that are in range of at least one positon

  for oh in ohs:                                  ### For each OH in ohs

    st = oh.intersecting_ohs    ### Get set of intersecting OHs' indices

    for idx in st:                         ### For each one of those ...

      ### ... remove any that do not intersect with all others

      st = st.intersection(ohs[idx].intersecting_ohs)

      if len(st) < Lmx:    ### Ignore this OH if set size goes below max
        break

    if len(st) >= Lmx:      ### Add this OH's set if size is max so far
      Lmx = len(st)
      st_subsets.add(tuple(sorted(st)))
      #st_subsets.add((Lmx,tuple(sorted(st)),))

    if ((oh.idx+1)%100): continue           ### Show progress while slow
    sys.stderr.write('{0}...'.format(oh.idx+1))
    sys.stderr.flush()

  sys.stderr.write('done\n')                ### Complete progress output
  sys.stderr.flush()

  ######################################################################
  ### At this point, st_subsets contains tuples, each of which contains
  ### the indices (into ohs) of OHs that mutually intersect one another

  Lmxtups = [t                               ### Select those tuples ...
             for t in st_subsets             ### ... from st_subsets ...
             if len(t)==Lmx               ### ... that are of length Lmx
            ]

  ### From the problem statement, "Find the coordinates that are in
  ### range of the largest number of nanobots. What is the shortest
  ### manhattan distance between any of those points and 0,0,0?"

  ### For each of those tuples with the maximum number of OH indices,
  ### calculate the maximum manhattan distance from the origin
  ### (OH.vzero) to the surface of any OH in that tuple, and use the
  ### minimum of those calculated maxima as the answer for Part II

  partII = min([max([ ohs[idx].md(OH.vzero)-ohs[idx].r
                      for idx in tup
                    ]
                   )
                for tup in Lmxtups
               ]
              )
    
  print('PartII:  {0}'.format(partII > 0 and partII or 0))
