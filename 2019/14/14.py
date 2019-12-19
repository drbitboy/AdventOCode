import os
import sys
import pickle
import intcode
import itertools

TERA = 1000000000000
FUEL,ORE = 'FUEL ORE'.split()

do_debug = 'DEBUG' in os.environ

########################################################################
def part1(dt,dt_need_arg=None,dt_have_arg=None):
  """
  Day 14 part 1:  TBD
  """

  if dt_need_arg is None: dt_need = dict(FUEL=1)
  else                  : dt_need = dt_need_arg

  if dt_have_arg is None: dt_have = dict()
  else                  : dt_have = dt_need_arg


  st_needkeys = list(dt_need.keys())
  while 1<len(st_needkeys) or not ('ORE' in dt_need):
    if do_debug: print(dict(dt_need=dt_need,dt_have=dt_have))
    for key in st_needkeys:
      if do_debug: print(dict(key=key))
      if ORE==key: continue
      if not (key in dt_have): dt_have[key] = 0
      if dt_have[key] < dt_need[key]:
        if do_debug: print(dict(dt_key=dt[key],zidtk=0 in dt[key]))
        quantum = dt[key][0]
        factor = ((dt_need[key]-dt_have[key]) + quantum - 1) / quantum
        if do_debug: print((key,quantum,factor,))
        for subkey in dt[key]:
          if not isinstance(subkey,str): continue
          assert subkey != key
          if not (subkey in dt_need): dt_need[subkey] = 0
          dt_need[subkey] += factor * dt[key][subkey]
        dt_have[key] += quantum * factor
      dt_have[key] -= dt_need[key]
      del dt_need[key]
    st_needkeys = list(dt_need.keys())
  return dt_need[ORE]

########################################################################
def part2(dt):
  """
  Day 14 part 2:  TBD
  """

  hifuel,hiore,lofuel,loore = 1,part1(dt,dt_need_arg=dict(FUEL=1)),0,0

  ### Double hi-fuel requirement until hi-ore required is greater than
  ### TERA (one trillion); saving previous hi-fuel and -ore requirements
  ### in lofuel and loore variables

  while hiore <= TERA:
    lofuel,loore = hifuel,hiore
    hifuel <<= 1
    hiore = part1(dt,dt_need_arg=dict(FUEL=hifuel))

  ### Binary search
  ### Invariants:  hiore > TERA; loore <= TERA

  while (hifuel-lofuel) > 1:
    midfuel = lofuel + ((hifuel-lofuel)>>1)
    midore = part1(dt,dt_need_arg=dict(FUEL=midfuel))
    if midore > TERA: hifuel,hiore = midfuel,midore
    else            : lofuel,loore = midfuel,midore
    
    
  return dict(fuel=lofuel,ore=loore)
########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  with open(fn,'r') as fin:
    dt = dict()
    for rawline in fin:
      def ik_split(tok):
        s_i,key = tok.strip().split()
        return key,int(s_i)

      toks = list(map(ik_split,rawline.replace('=>',',').split(',')))
      product,i = toks.pop()
      assert not (product in dt)
      dt[product] = dict(((0,i,),))
      dt[product].update(dict(toks))

  if not bn.startswith('sample_input_part2_'):
    print(dict(part1=part1(dt)))

  if not bn.startswith('sample_input_part1_'):
    print(dict(part2=part2(dt)))

