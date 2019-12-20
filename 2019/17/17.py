import os
import sys
import pickle
import intcode
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
  """Add 2D unit vector of direction to 2D position"""
  return (pos[0]+tp_dir[2],pos[1]+tp_dir[3],)

def manh(pos0,pos1):
   """Manhattan Distance between two 2D positions"""
   return abs(pos0[0]-pos1[0]) + abs(pos0[1]-pos1[1])

assert 15==manh((10,20,None,),('a',1,26,None,)[1:])

########################################################################
def explore(instance, tp_pos, st_visited, st_blocked, found2):
  """
  Recursive depth-first search of all adjacent non-blocked spots

  """
  st_visited.add(tp_pos)
  Lo = len(instance.outputs)
  for dir in tp_dirs:

    tp_new_pos = move(tp_pos,dir)

    if (tp_new_pos) in st_visited: continue
    if (tp_new_pos) in st_blocked: continue

    instance.add_input_data(dir[1],state_must_be_init=False)
    instance.run()
    assert instance.state==intcode.INSTANCE.READWAIT
    Lo += 1
    assert len(instance.outputs)==Lo
    result = instance.outputs[-1]

    if not result:
      st_blocked.add(tp_new_pos)
      continue

    if 2==result: found2 = tp_new_pos

    found2 = explore(instance,tp_new_pos,st_visited,st_blocked,found2)[-1]
    Lo = len(instance.outputs)

    back_dir = dt_dirs[(dir[0]+2)%4]
    instance.add_input_data(back_dir[1],state_must_be_init=False)
    instance.run()
    Lo += 1
    assert len(instance.outputs)==Lo
    assert instance.outputs[-1]
    assert move(tp_new_pos,back_dir)==tp_pos
  
  return st_visited,st_blocked,found2


########################################################################
def wall_follower(instance):

  """
  Wall follower code:  assumes all paths are one unit wide

  """

  st_visited = set()
  st_blocked = set()

  tp_current_dir = dt_dirs[0]
  tp_position = (0,0,)

  start_direction = tp_current_dir[4]
  start_position = tp_position

  ### Walk North to a wall

  while instance.state==intcode.INSTANCE.READWAIT:
    st_visited.add(tp_position)

    if instance.outputs:
      if not instance.outputs[-1]:
        ### Found a wall
        st_blocked.add(move(tp_position,tp_current_dir))
        break
      ### Update position
      tp_position = move(tp_position,tp_current_dir)

    instance.add_input_data(tp_current_dir[1],state_must_be_init=False)
    instance.run()

  assert instance.state==intcode.INSTANCE.READWAIT

  ### Right-wall-follower maze algorithm
  ### - Invariant at top of this loop:  facing a wall

  while 2!=instance.outputs[-1] and instance.state==intcode.INSTANCE.READWAIT:

    ################################
    ### 1) Test invariant

    Lo = len(instance.outputs)
    instance.add_input_data(tp_current_dir[1],state_must_be_init=False)
    instance.run()
    assert instance.state==intcode.INSTANCE.READWAIT
    Lo += 1
    assert len(instance.outputs)==Lo
    assert not instance.outputs[-1]


    ################################
    ### 2) Turn left, check infinite loop, try to take a step

    tp_current_dir = turn_lt(tp_current_dir)
    ### 2.1) Ensure we did not return to starting state
    assert start_position!=tp_position or start_direction!=tp_current_dir[4]
    instance.add_input_data(tp_current_dir[1],state_must_be_init=False)
    instance.run()
    Lo += 1
    assert len(instance.outputs)==Lo

    ################################
    ### 3) If we hit a wall in this new direction, invariant is valid,
    ###    add blocked spot, repeat loop

    if not instance.outputs[-1]:
      st_blocked.add(move(tp_position,tp_current_dir))
      continue

    ### 4) We did not hit a wall, update the position, add visited spot
    tp_position = move(tp_position,tp_current_dir)
    st_visited.add(tp_position)
    assert start_position!=tp_position or start_direction!=tp_current_dir[4]
    ### 4.1) Exit loop if we found 2
    if 2==instance.outputs[-1]: break
    assert 1==instance.outputs[-1]

    ################################
    ### 5) We took a step, but did not find 2:
    ###    - Ensure a wall is on the right before repeating loop:
    ###      - Turn back to the right and try to take a step
    ###        - 5.1) Continue (repeat loop) if (same) wall is there
    ###        - If no wall, then we turned a corner:
    ###          - 5.2) Update position
    ###          - 5.3) Turn right to face wall
    ###          - Invariant should be valid after right turn (5.3)

    tp_current_dir = turn_rt(tp_current_dir)
    assert start_position!=tp_position or start_direction!=tp_current_dir[4]
    instance.add_input_data(tp_current_dir[1],state_must_be_init=False)
    instance.run()
    Lo += 1
    assert len(instance.outputs)==Lo

    ### 5.1) if we hit a wall, add blocked spot and do nothing else this pass
    if not instance.outputs[-1]:
      st_blocked.add(move(tp_position,tp_current_dir))
      continue

    ### 5.2) Update position, add visited spot
    tp_position = move(tp_position,tp_current_dir)
    st_visited.add(tp_position)
    assert start_position!=tp_position or start_direction!=tp_current_dir[4]
    if 2==instance.outputs[-1]: break
    assert 1==instance.outputs[-1]

    ### 5.3) Turn right to wall
    tp_current_dir = turn_rt(tp_current_dir)
    assert start_position!=tp_position or start_direction!=tp_current_dir[4]

  assert 2==instance.outputs[-1]
  if do_debug:
    print(instance.outputs[-10:])
    print((instance.state,intcode.INSTANCE.READWAIT,))

  return st_visited,st_blocked,tp_position

def bfs15(st_visited,st_blocked,found2,start_xy=(0,0,)):
  """
  Breadth-First Search of shortest path from (0,0,) to found2
  via adjacent nodes (x,y pairs) i.e. equal weights

  """
  if do_debug: print(len(st_visited),len(st_blocked),found2)
  dt_dists = dict()         ### key is (x,y) position; value is distance
  qu = queue.Queue()        ### FIFO
  dt_dists[start_xy] = 0    ### Initial position is at distance zero
  qu.put(start_xy)          ### Put initial position onto queue

  while not qu.empty():               ### While xys remain in queue..
    xy = qu.get()                     ### Get first xy (shortest path)
    if xy==found2:                    ### If xy is the found2 target,
      return found2,dt_dists[found2]  ###   then return it & distance
    xy_dist = dt_dists[xy]            ### Save path distance to xy
    for dir in tp_dirs:               ### For each direction ...
      new_xy = move(xy,dir)           ###   Calc xy' in that direction
      if not (new_xy in st_visited):  ###   If xy' is not in graph,
         continue                     ###     then skip xy'
      if new_xy in dt_dists:          ###   If xy' has shorter distance
        continue                      ###     already, then skip xy'
      dt_dists[new_xy] = xy_dist + 1  ### Give xy' a distance 1 past xy
      qu.put(new_xy)                  ### Add xy' to queue

  return start_xy,xy_dist             ### Time to fill entire graph

########################################################################
def part1(icode):
  """
  Day 15 part 1

  Create an INTCODE INSTANCE, then run it

  """
  instance = intcode.INSTANCE(icode)
  instance.run()
  print('\n=====\n{0}\n====='.format(''.join([chr(i)
                                              for i in instance.outputs
                                             ]).rstrip('\n')
                                    ))


########################################################################
def part2(icode):
  """
  Day 15 part 2

  """
  pass


########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  ### Global Intcode program
  icode = intcode.INTCODE(fn)

  if not bn.startswith('sample_input_part2_'):
    ### Get outputs from Intcode instance
    dt_part1_results = part1(icode)
    print(dict(part1=dt_part1_results))
    #with open('15.pickle','wb') as fin:
    #  pickle.dump(dict(explore_results=explore_results
    #                  ,wall_results=wall_results
    #                  )
    #             ,fin
    #             )

  if not bn.startswith('sample_input_part1_'):
    dt_part2_results = part2(icode)
    print(dict(part2=dt_part2_results))
