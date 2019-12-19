"""
Usage:  clear ; python play13.py

Play game recorded in 13.pickle by 13.py and input.txt on ANSI terminal.

"""
import os
import sys
import time
import pickle

if "__main__" == __name__:
  CSI='{0}['.format(chr(27))
  cs = ' X*-o'

  def w(x,y,typ):
    if -1==x and 0==y:
      x = 50
      y = 10
      val = typ
    elif -2==x and 0==y:
      x = 50
      y = 9
      val = 'Score:'
    else:
      x += 3
      y += 3
      val = cs[typ]
    sys.stdout.write('{0}{1};{2}H{3}'.format(CSI,y,x,val))
    sys.stdout.flush()
    time.sleep(0.01)

  with open('13.pickle','rb') as fin:
    result = pickle.load(fin)
    lt_outputs = result['lt_outputs']
    dt_inputs = result['dt_inputs']

  Lo = len(lt_outputs)

  w(-2,0,None)
  for i in range(0,Lo,3): w(*lt_outputs[i:i+3])
  
