import os
import sys
try: import Queue as queue
except: import queue

### Debug via environment variable DEBUG
### e.g. BASH:  DEBUG= python NN.py

do_debug = 'DEBUG' in os.environ

north,east,south,west = 'north east south west'.split()

### 0:  0-3 internal directions; +1 turns right
### 1:  1-4 Intcode directions
### 2,3:  2D unit vector; (horizontal (positive right), vertical (positive down),)
### 4:  direction name


tp_dirs = ((0,1,0,-1,north,)
          ,(1,4,1,0,east,)
          ,(2,2,0,1,south,)
          ,(3,3,-1,0,west,)
          ,)
Rdir = range(len(tp_dirs))
def keytup(tup): return tup[0],tup
dt_dirs = dict(map(keytup,tp_dirs))

for key in dt_dirs.keys(): dt_dirs[dt_dirs[key][0]] = dt_dirs[key]

def turn(tp_dir,left):
  """Turn left or right"""
  return dt_dirs[(tp_dir[0] + (left and 3 or 1)) % 4]

def turn_rt(tp_dir):
  """Turn right"""
  return turn(tp_dir,False)

def turn_lt(tp_dir):
  """Turn left"""
  return turn(tp_dir,True)

def move(pos,tp_dir):
  """Add 2D vector to 2D position in pos[:2]; maintain extra data"""
  return (pos[0]+tp_dir[2]  ### Offset wrt to X position in pos[0]
         ,pos[1]+tp_dir[3]  ### Offset wrt to Y position in pos[1]
         ,)+tuple(pos[2:])  ### Keep any data after that


chash,cdot,cat,ccr,cnl = '#.@\r\n'
ccrnl = ccr + cnl

########################################################################
def mask_bit(c):
  if c==cat or c==cdot: return 0
  if c==chash: return 1
  clower = c.lower()
  assert clower!=c.upper()
  return 2 << (ord(clower) - ord('a'))

hash_bit = mask_bit(chash)


########################################################################
def bfs18(ltb):
  """
  One argument:  ltb, and instance of class LTB, representing the board

  Breadth-First Search (BFS) of shortest path from start to get all keys
  via adjacent nodes ((x,y,mask,) triples) i.e. equal weights

  A mask comprises bits representing each door or hash (wall); doors may
  be unlocked once its key is obtained; walls cannot be unlocked.

  The board ltb, which is an instance of class LDB and a sub-class of
  list, has a value for each position on the board with one bit set if
  there is a door, a lock for a door, or a hash (wall), at that position
  position.  A door and its corresponding key have the same bit set;
  keys may be distinguished because they are in the set ltb.keys, with
  lookup (x,y,bit).

  The XY triples (X,Y,Mask,) below represent some state within the
  search graph:
  - the tuple (X,Y,) represents the column and row i.e. position,
    - so ltb[Y][X] either is zero, or contains a bit representing the
      mask for any wall, key or door at that position;
  - the integer Mask has bits set for which the state has no keys,
    - so this mask will be set initially to all 1s for all keys, plus
      one bit (hash_bit) set for walls,
    - and Mask bits will be cleared when the state passes over a key in
      ltb.

  The BFS algorithm terminates when all keys have been found, in which
  case the state's mask will be hash_bit i.e. only the bit for the wall
  will be set.

  """

  ################################# Helper methods

  XYM = lambda p,m: p[:2]+(m,)  ### Calculate triple:  (X,Y,Mask,)

  def Ltb(p):                   ### Get LTB data for this xy position p
    return ltb[p[1]][p[0]]

  def Lkey(p):                  ### Is this an LTB key (lower-case)?
    lu = XYM(p,Ltb(p))          ###   Build lookup for dict ltb.keys
    return lu in ltb.keys       ###   Return True if this is a key

  ############################### Setup BFS algorithm

  FM = ltb.full_mask          ### Initialize local Mask, with no keys
  P0 = ltb.start              ### Initialize position triple (X,Y,Mask,)
  start_xy = XYM(P0,FM)       ### Initialize triple, no keys

  dt_d = dict()               ### Lookup=(x,y,mask,); value=distance
  qu = queue.Queue()          ### FIFO

  dt_d[start_xy] = 0          ### Initial position at distance zero
  qu.put(start_xy)            ### Push initial position onto queue

  ################################# Start BFS algorithm

  while not qu.empty():       ### While xy triples remain in queue ...
    xy = qu.get()             ### Pop first xy (shortest path), and mask
    M = xy[2]                 ### Extract mask from xy
    if M==hash_bit:           ### If all keys were found, then terminate
      return xy,dt_d[xy]      ###   by returning position & distance
    xy_d = dt_d[xy]           ### Store path distance to xy in local var
    for dir in tp_dirs:       ### For each direction ...
      xyp = move(xy,dir)      ###   Calculate xy' in that dir, keep mask
      lbit = Ltb(xyp)         ###   Get 1-bit LTB mask at xy position
      if (lbit & M):          ###   If LTB mask intersects key not held,
        if lbit==hash_bit:    ###     Then if there is a hash wall here,
          continue            ###       then do nothing
        lu = XYM(xyp,lbit)    ###   Calculate LTB lookup, 1-bit mask
        if lu in ltb.keys:    ###   If this is a key for a door (lock),
          b = xyp[2] ^ lbit   ###     Then calculate mask with bit clear
          xyp = XYM(xyp,b)    ###     And update xy' mask (pick up key)
        else:                 ###   Else xy' is a door & we have no key,
          continue            ###     So do nothing
      if xyp in dt_d:         ###   If xy' has shorter distance already,
        continue              ###     Then skip xy'
      dt_d[xyp] = xy_d + 1    ### Give xy' a distance 1 past xy
      qu.put(xyp)             ### Add xy' to queue

  return (-1,-1,0,), -1  ### There is no path:  return fake XYM,dist


########################################################################
class LTB(list):

  def __init__(self,fn):

    self.ascii = list()

    self.full_mask,self.height,self.keys = hash_bit,0,set()

    with open(fn,'r') as fin:
      for rawrow in fin:

        modrow = rawrow.strip(ccrnl)
        if not modrow: break
        if not self.height: self.width = len(modrow)
        assert self.width == len(modrow)

        lt_row,col = list(),-1

        for c in modrow:

          col += 1

          mbc = mask_bit(c)
          lt_row.append(mbc)

          if cat==c: self.start = (modrow.find(cat),self.height,)

          if not mbc: continue

          self.full_mask |= mbc
          if c.upper()!=c: self.keys.add((col,self.height,mbc,))

        self.append(lt_row)
        self.ascii.append(modrow)
        self.height += 1


########################################################################
def part1(fn):
  """
  Day 18 part 1

  """

  ltb = LTB(fn)

  if do_debug:
    for row in ltb.ascii: print(row)
    print((ltb.width,ltb.height,ltb.start,ltb.full_mask,'{0:x}'.format(ltb.full_mask),))
    print(ltb.keys)

  return dict(zip('xy_end shortest_path'.split(),bfs18(ltb)))


########################################################################
def part2(fn):
  """
  Day 15 part 2

  """
  return None
  (dt_part1_results
  ,(explore_visited,explore_blocked,explore_found2)
  ,(wall_visited,wall_blocked,wall_found2)
  ,) = part1(icode)

  return dict(explore_results=bfs15(explore_visited
                                   ,explore_blocked
                                   ,(None,None,)
                                   ,start_xy=explore_found2
                                   )
             ,wall_results=bfs15(wall_visited
                                   ,wall_blocked
                                   ,(None,None,)
                                   ,start_xy=wall_found2
                                   )
             )


########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  if not bn.startswith('sample_input_part2_'):
    ### Get outputs from Intcode instance
    dt_part1_results = part1(fn)
    print(dict(part1=dt_part1_results))

  if not bn.startswith('sample_input_part1_'):
    dt_part2_results = part2(fn)
    print(dict(part2=dt_part2_results))
