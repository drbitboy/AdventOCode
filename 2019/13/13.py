import os
import sys
import intcode

black = 0
white = 1

########################################################################
def part1():
  """
  Day 13 part 1

  """
  global icode

  ### Create an INTCODE INSTANCE, then run it
  instance = intcode.INSTANCE(icode,lt_inputs_arg=[])
  instance.run()
  assert intcode.INSTANCE.FINI==instance.state

  return instance.outputs

########################################################################
def part2():
  """
  Day 13 part 2

  """
  global icode

  inputs = [0]
  dt_i = dict()
  while True:
    ### Create an INTCODE INSTANCE, then run it
    instance = intcode.INSTANCE(icode,lt_inputs_arg=[])
    instance.vm[0] = 2
    instance.add_input_data(*inputs)
    instance.run()
    Llast = len(instance.outputs)
    if not dt_i:
      Lo = len(instance.outputs)
      while True:
        Lo -= 3
        if instance.outputs[Lo+2]==3:
          paddlex,paddley,typ=paddle=instance.outputs[Lo:Lo+3]
          break
    print('\n========================================================================')
    print(('Start',Llast,instance.outputs[-30:],))
    print(dict(paddle=paddle))

    while intcode.INSTANCE.READWAIT==instance.state:
      Lo = len(instance.outputs)
      print(('Read',Lo,instance.outputs[Llast:],))
      Llast = Lo
      instance.add_input_data(dt_i.get(Lo,0),state_must_be_init=False)
      instance.run()

    Lo = len(instance.outputs)

    tail = instance.outputs[-600:]
    adjust = None
    while (adjust is None) or adjust:
      typ,y,x = tail.pop(),tail.pop(),tail.pop()
      if typ==4:
        if not (adjust is None):
          extra6 -= 6
          if adjust > 0:
            adjust  += -1
            paddlex += +1
            dt_i[Lo+extra6] = +1
          else:
            adjust  += +1
            paddlex += -1
            dt_i[Lo+extra6] = -1
          print(dict(adjust=adjust,paddlex=paddlex,Lo=Lo,Loplus=Lo+extra6,dtnew=dt_i[Lo+extra6]))
        elif paddley==y:
          adjust = x - paddlex
          assert adjust
          extra6 = 6 * abs(adjust)
          print(dict(adjust=adjust,x=x,paddlex=paddlex,extra6=extra6))
      Lo -= 3

    print(('Fini',Lo,instance.outputs[Llast:],))

    assert intcode.INSTANCE.FINI==instance.state

    sys.stdout.flush()

  return instance.outputs

########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  icode = intcode.INTCODE(fn)

  if not bn.startswith('sample_input_part2_'):
    outputs = part1()
    L = len(outputs)
    d = dict([(i,0,) for i in range(5)])
    for i in range(0,L,3):
      d[outputs[i+2]] += 1
    print(dict(part1=d))

  if not bn.startswith('sample_input_part1_'):
    outputs = part2()


