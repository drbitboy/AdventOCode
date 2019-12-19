import os
import sys
import pickle
import intcode

### Debug via environment variable DEBUG
### e.g. BASH:  DEBUG= python NN.py

do_debug = 'DEBUG' in os.environ


########################################################################
def part1(icode):
  """
  Day 13 part 1

  Create an INTCODE INSTANCE, then run it; this will draw the board by
  loading (X,Y,Type) triplets into list instance.outputs


  """


  instance = intcode.INSTANCE(icode,lt_inputs_arg=[])
  instance.run()
  assert intcode.INSTANCE.FINI==instance.state

  return instance.outputs

########################################################################
def part2(icode):
  """
  Day 13 part 2

  Repeatedly run program.  As each round is lost because ball passes the
  paddle, find where that occurred and add joystick movement as needed
  via dt_i

  """

  ### dt_:  dict of joystick non-zero moves
  ### dt_scores:  dict of counts of scores, for detecting infinite loops

  dt_i,dt_scores = dict(),dict()

  ### Initial input:  do nothing

  inputs = [0]

  while True:

    ### Create an INTCODE INSTANCE, put two quarters into coin slot
    ### (memory location 2), add one input datum to dt_i, then run program

    instance = intcode.INSTANCE(icode,lt_inputs_arg=[])
    instance.vm[0] = 2
    instance.add_input_data(*inputs)
    instance.run()

    ### Save last output pointer
    Llast = len(instance.outputs)

    ### If no joystick inputs yet, save initial paddle position

    if not dt_i:
      Lo = len(instance.outputs)
      while True:
        Lo -= 3
        if instance.outputs[Lo+2]==3:
          ### Type 3 is paddle position; save X and Y
          paddlex,paddley=paddle=instance.outputs[Lo:Lo+2]
          paddle_toggle = paddley + paddley - 1
          break

    if do_debug:
      print('\n========================================================================')
      print(('Start',Llast,instance.outputs[-30:],))
      print(dict(paddle=paddle))

    ### Run program as long as it is waiting for input
    ### - If it is not waiting for input, it ended, either because ball
    ###   passed paddle, or all blocks are gone

    while intcode.INSTANCE.READWAIT==instance.state:
      Lo = len(instance.outputs)
      if do_debug: print(('Read',Lo,instance.outputs[Llast:],))
      Llast = Lo
      instance.add_input_data(dt_i.get(Lo,0),state_must_be_init=False)
      instance.run()

    if do_debug: print(('Endw',dict(state=instance.state),))

    x,y,score = instance.outputs[-3:]
    if -1==x and 0==y and score>0:

      ### End of successful round:  all blocks are gone; pickle outputs
      ### for play13.py; exit outer [while True] loop

      with open('13.pickle','wb') as fout:
        pickle.dump(dict(lt_outputs=instance.outputs,dt_inputs=dt_i),fout)

      ### Return score and outputs
      return score,instance.outputs

    ### Copy last 200 output triples list (tail); find where ball exited
    ### field, add joystick movement to paddle to catch it next time

    tail = instance.outputs[-600:]

    ### Variable adjust will be None until a ball position on row
    ### [paddley] is found; then ad will be a non-zero integer that is
    ### incremented or decremented for each previous INSTANCE.READWAIT
    ### occurrence, until it hits zero

    adjust = None

    ### Loop until adjust is zero

    Lo = len(instance.outputs)

    while (adjust is None) or adjust:

      ### Get last (x,y,type) triple

      typ,y,x = tail.pop(),tail.pop(),tail.pop()

      if typ==4:

        ### Triple expresses a ball position

        if not (adjust is None):

          ### Variable adjust is non-zero integer; Lo is length of
          ### instance.outputs for this ball position and when
          ### INSTANCE.READWAIT occurred in last run
          ### - Variable extra6 accounts for paddle movement data
          ###   in next run

          extra6 -= 6

          ### - Move paddle at INSTANCE.READWAIT when
          ###   len(instance.outputs) will be (Lo+extra6)

          delta = adjust > 0 and +1 or -1
          adjust  -= delta
          paddlex += delta
          dt_i[Lo+extra6] = delta

          if do_debug: print(dict(adjust=adjust,paddlex=paddlex,paddley=paddley,Lo=Lo,Loplus=Lo+extra6,dtnew=dt_i[Lo+extra6]))

        elif paddley==y:

          ### Variable adjust is None; initialize joystick variables;
          ### ball is at x,paddley; paddley is on or above paddle row
          ### - x is ball position
          ### - paddlex is paddle position
          ### - Set adjust to how much paddle must move
          ### - Add 6 positions per move to account for movement
          ###   of paddle in instance.outputs list during next loop
          adjust = x - paddlex
          extra6 = 6 * abs(adjust)
          if do_debug:
            print(dict(adjust=adjust,x=x,paddlex=paddlex,extra6=extra6))
            sys.stdout.flush()

          assert adjust

      ### Decrement output pointer

      Lo -= 3

    if do_debug:
      Lo = len(instance.outputs)
      print(('Fini',Lo,instance.outputs[Llast:],))

    Lo = len(instance.outputs)

    ### Find last non-zero score

    score = 0
    while (Lo>10000) and (not score):
      x,y,typ = instance.outputs[Lo-3:Lo]
      if (-1==x) and (0==y): score = typ
      Lo -= 3


    if score:

      ### Keep track of how many times this non-zero score occurred

      if score in dt_scores: dt_scores[score] += 1
      else                 : dt_scores[score]  = 1

      ### If it occurred 20 times, adjust paddley parameter that
      ### controls paddle adjustment above

      if score and (dt_scores[score] > 19):
        dt_scores[score] = 0
        paddley = paddle_toggle - paddley
        if do_debug:
          print(('Score',dict(score=score,score_count=dt_scores[score],paddley=paddley),))

    assert intcode.INSTANCE.FINI==instance.state

    sys.stdout.flush()

    ### End of outer [while True] loop
    ####################################################################


########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  ### Global Intcode program
  icode = intcode.INTCODE(fn)

  if not bn.startswith('sample_input_part2_'):
    ### Get outputs from Intcode instance
    outputs = part1(icode)

    ### List [outputs] comprises (X,Y,Type) triples.

    ### - Build dictionary to count each type
    d = dict([(i,0,) for i in range(5)])
    
    ### - Loop over triple, count each type
    L = len(outputs)
    for i in range(0,L,3):
      d[outputs[i+2]] += 1

    ### - Print result; d[2] is number of blocks required by
    ###   2019/day/13/ part 1
    print(dict(part1=d[2],d=d))


  if not bn.startswith('sample_input_part1_'):
    score,outputs = part2(icode)
    print(dict(part2=score))
