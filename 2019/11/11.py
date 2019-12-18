import os
import sys
import intcode

black = 0
white = 1

########################################################################
def run_11(start_color):
  """
  Day 11 part 1:  amplifiers in series with phases and inputs,
                 feedback last instance to first,
                 one pass each
 
  """
  global icode

  ### Create an INTCODE INSTANCE
  instance = intcode.INSTANCE(icode,lt_inputs_arg=[])

  st_whites,xypair,dir,output_ptr = set(),(0,0,),0,0
  st_painted_once = set()

  if start_color==white: st_whites.add(xypair)

  instance.run()

  while intcode.INSTANCE.READWAIT==instance.state:
    Lo = len(instance.outputs)
    if (Lo-2) == output_ptr:

      color,turn = instance.outputs[-2:]
      output_ptr += 2

      if white==color: st_whites.add(xypair)
      else           : st_whites.discard(xypair)
      st_painted_once.add(xypair)

      dir = (dir + 4 + (turn and 1 or -1)) % 4

      if 0==dir  : xypair = (xypair[0]+0,xypair[1]-1,)
      elif 1==dir: xypair = (xypair[0]+1,xypair[1]+0,)
      elif 2==dir: xypair = (xypair[0]+0,xypair[1]+1,)
      else       : xypair = (xypair[0]-1,xypair[1]+0,)

    else:
      assert not instance.outputs

    instance.add_input_data(*[xypair in st_whites and white or black]
                           ,state_must_be_init=False
                           )
    instance.run()

  xwhites,ywhites = zip(*st_whites)
  xmin = min(xwhites)
  ymin = min(ywhites)
  width = 1 + max(xwhites) - xmin
  height = 1 + max(ywhites) - ymin
  arr = [[' ']*width for i in range(height)]
  print((width,height,xmin,ymin,))
  print((len(arr[0]),len(arr),))
  for x,y in st_whites:
    print((x,y,))
    arr[y-ymin][x-xmin] = '@'
  return len(st_painted_once),st_whites,'\n'.join([''.join(row) for row in arr])


def run_11_part2():
  pass

########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  icode = intcode.INTCODE(fn)

  if not bn.startswith('sample_input_part2_'):
    print(dict(part1=run_11(black)[0]))

  if not bn.startswith('sample_input_part1_'):
    count2,stwhites,s_arr = run_11(white)
    print(dict(part2=count2))
    print(s_arr)


