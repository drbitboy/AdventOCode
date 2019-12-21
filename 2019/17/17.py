import os
import sys
import pickle
import intcode
import functions
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


cnorth,ceast,csouth,cwest,cnl,chash,cdot = sall = '^>v<\n#.'
chash3 = [chash] * 3
sdirs = sall[:4]


tp_dirs = ((0,1,0,-1,north,)
          ,(1,4,1,0,east,)
          ,(2,2,0,1,south,)
          ,(3,3,-1,0,west,)
          ,)
Rdir = range(len(tp_dirs))
def keytup(tup): return tup[0],tup
dt_dirs = dict(map(keytup,tp_dirs))

dt_dirs.update(dict([(eval('c{0}'.format(tp_dir[-1])),tp_dir,) for tp_dir in tp_dirs]))


########################################################################
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


########################################################################
def part1(icode):
  """
  Day 15 part 1

  Create an INTCODE INSTANCE, then run it

  """
  instance = intcode.INSTANCE(icode)
  instance.run()

  lt_rows = list()
  lt_row = list()
  result,height = 0,0

  for i in instance.outputs:

    c = chr(i)
    assert c in sall

    if cnl==c:
      if not lt_row: break
      if lt_rows: assert width==len(lt_row)
      else      : width = len(lt_row)
      lt_rows.append(lt_row)
      height = len(lt_rows)
      lt_row = list()

    else:
      pos = len(lt_row)
      if c in sdirs:
        start_xy = pos,height
      elif 1<height and chash==c:
        c2up =lt_rows[-2][pos]
        c1up =lt_rows[-1][pos-1:pos+2]
        if (chash==c2up) and (chash3==c1up):
          result += ((height-1) * pos)
      lt_row.append(c)

  assert not lt_row

  return dict(result=result
             ,start_xy=start_xy
             ,lt_rows=lt_rows
             ,instance_state=instance.state
             )


########################################################################
def get_c(lt_rows,xy,dir=None):
  height,width = len(lt_rows),len(lt_rows[0])
  x,y = dir is None and xy or move(xy,dir)
  if x<0 or y<0: return ''
  if x>=width or y>=height: return ''
  return lt_rows[y][x]


########################################################################
def part2(icode):
  """
  Day 15 part 2

  """

  dt_part1_results = part1(icode)

  lt_rows = dt_part1_results['lt_rows']
  start_xy = dt_part1_results['start_xy']
  current_xy = tuple(list(start_xy))
  current_c = get_c(lt_rows,current_xy)
  start_dir = dt_dirs[current_c]
  current_dir = tuple(list(start_dir))
  assert not (current_xy is start_xy)
  assert not (current_dir is start_dir)

  linear_steps = 0
  lt_commands = list()

  while True:

    if do_debug: print(dict(lt_commands_last4=lt_commands[-4:],linear_steps=linear_steps,current_c=current_c,current_xy=current_xy,current_dir=current_dir))

    if chash==get_c(lt_rows,current_xy,current_dir):
      linear_steps += 1
      current_xy = move(current_xy,current_dir)
      current_c = chash
      continue

    if 0<linear_steps: lt_commands.append('{0}'.format(linear_steps))

    linear_steps = False

    for f in (turn_rt,turn_lt,):
      new_dir = f(current_dir)
      if chash==get_c(lt_rows,current_xy,new_dir):
        current_dir = new_dir
        current_xy = move(current_xy,new_dir)
        linear_steps = 1
        current_c = chash
        lt_commands.append(f is turn_rt and 'R' or 'L')
        break

    if do_debug: print(dict(linear_steps=linear_steps,Llt_commands=len(lt_commands)))

    if linear_steps: continue
    if lt_commands: break

    ### Try opposite direction via two left turns

    current_dir = turn_lt(turn_lt(current_dir))
    assert chash==get_c(lt_rows,current_xy,current_dir)
    lt_commands.extend(list('LL'))

  s_commands = ','.join(lt_commands)

  dt_fs = functions.functions
  keys = list(dt_fs.keys())
  main_routine = s_commands
  for key in keys:
    s_value = dt_fs[key]
    assert 20 > len(s_value)
    main_routine = main_routine.replace(s_value,key)
  main_routine 
  rtn = dict(s_commands = s_commands
            ,main_routine = main_routine
            )
  rtn .update(dt_fs)

  return rtn


########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  ### Global Intcode program
  icode = intcode.INTCODE(fn)

  if not bn.startswith('sample_input_part2_'):
    ### Get outputs from Intcode instance
    dt_part1_results = part1(icode)
    with open('17.pickle','wb') as fin:
      pickle.dump(dt_part1_results,fin)
    lt_rows = dt_part1_results['lt_rows']
    del dt_part1_results['lt_rows']
    if do_debug:
      print('\n{1}\n{0}\n{1}'.format(cnl.join([''.join([c for c in lt_row])
                                               for lt_row in lt_rows
                                              ]).rstrip(cnl)
                                    ,'='*72
                                    ))
    print(dict(part1=dt_part1_results))

  if not bn.startswith('sample_input_part1_'):
    dt_part2_results = part2(icode)
    print(dict(part2=dt_part2_results))
